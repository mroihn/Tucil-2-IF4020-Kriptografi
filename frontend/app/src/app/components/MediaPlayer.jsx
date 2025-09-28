'use client';
import React, { useState, useEffect } from 'react';
import { Play, Pause, FileAudio } from 'lucide-react';

const MediaPlayer = ({ label, audio, audioRef }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlayback = () => {
    if (!audio || !audioRef?.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setProgress(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    const newTime = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
      setProgress(newTime);
    }
  };

  // Reset when audio ends
  const handleEnded = () => {
    setIsPlaying(false);
    setProgress(0);
  };

  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10 mt-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <FileAudio className="w-6 h-6 text-blue-300" />
          <div>
            <p className="text-white font-medium">{label}</p>
            <p className="text-white/60 text-sm">
              {audio ? audio.name : 'No audio loaded'}
            </p>
          </div>
        </div>

        <button
          onClick={togglePlayback}
          className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg"
          disabled={!audio}
        >
          {isPlaying ? (
            <Pause className="w-6 h-6 text-white" />
          ) : (
            <Play className="w-6 h-6 text-white ml-0.5" />
          )}
        </button>
      </div>

      {/* Progress bar */}
      {audio && (
        <div className="mt-4">
          <input
            type="range"
            min="0"
            max={duration}
            step="0.1"
            value={progress}
            onChange={handleSeek}
            className="w-full accent-blue-500"
          />
          <div className="flex justify-between text-xs text-white/60 mt-1">
            <span>{formatTime(progress)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      )}

      {audio && (
        <audio
          ref={audioRef}
          src={audio.url}
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={handleEnded}
          style={{ display: 'none' }}
        />
      )}
    </div>
  );
};

// helper: format seconds -> mm:ss
function formatTime(time) {
  if (isNaN(time)) return '0:00';
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export default MediaPlayer;
