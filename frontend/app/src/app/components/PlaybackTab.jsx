'use client';
import React from 'react';

const PlaybackTab = ({
  coverAudio,
  stegoAudio,
  currentAudio,
  setCurrentAudio,
  isPlaying,
  togglePlayback,
  coverAudioRef,
  stegoAudioRef,
  setIsPlaying,
}) => {
  return (
    <div className="p-6 space-y-4 rounded-2xl shadow-lg bg-slate-800/60 border border-slate-700">
      <h2 className="text-2xl font-semibold text-white">Playback</h2>

      <div className="flex gap-4">
        {/* Cover Audio */}
        {coverAudio && (
          <div className="flex flex-col items-center">
            <audio
              ref={coverAudioRef}
              src={URL.createObjectURL(coverAudio)}
              onPlay={() => {
                setCurrentAudio('cover');
                setIsPlaying(true);
              }}
              onPause={() => setIsPlaying(false)}
              controls
            />
            <button
              onClick={() => togglePlayback('cover')}
              variant={currentAudio === 'cover' ? 'default' : 'secondary'}
              className="mt-2"
            >
              {isPlaying && currentAudio === 'cover' ? 'Pause' : 'Play'} Cover
            </button>
          </div>
        )}

        {/* Stego Audio */}
        {stegoAudio && (
          <div className="flex flex-col items-center">
            <audio
              ref={stegoAudioRef}
              src={URL.createObjectURL(stegoAudio)}
              onPlay={() => {
                setCurrentAudio('stego');
                setIsPlaying(true);
              }}
              onPause={() => setIsPlaying(false)}
              controls
            />
            <button
              onClick={() => togglePlayback('stego')}
              variant={currentAudio === 'stego' ? 'default' : 'secondary'}
              className="mt-2"
            >
              {isPlaying && currentAudio === 'stego' ? 'Pause' : 'Play'} Stego
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaybackTab;
