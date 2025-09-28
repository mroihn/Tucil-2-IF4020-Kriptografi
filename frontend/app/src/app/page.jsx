'use client';
import React, { useState, useRef, useEffect } from 'react';
import { Upload, Play, Pause, Download, FileAudio, Lock, Unlock, Settings, Calculator, Eye, EyeOff } from 'lucide-react';
import Header  from './components/Header';
import EmbedTab from './components/EmbedTab';

const AudioSteganographyApp = () => {
  const [activeTab, setActiveTab] = useState('embed');
  const [coverAudio, setCoverAudio] = useState(null);
  const [secretMessage, setSecretMessage] = useState(null);
  const [stegoAudio, setStegoAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudio, setCurrentAudio] = useState('cover');
  // const [useEncryption, setUseEncryption] = useState(false);
  // const [useRandomStart, setUseRandomStart] = useState(false);
  // const [nLSB, setNLSB] = useState(1);
  const [stegoKey, setStegoKey] = useState('');
  const [extractedMessage, setExtractedMessage] = useState(null);
  const [showKey, setShowKey] = useState(false);
  const [fileName, setFileName] = useState('');

  const coverAudioRef = useRef(null);
  const stegoAudioRef = useRef(null);
  const currentAudioRef = useRef(null);

  useEffect(() => {
    if (currentAudio === 'cover' && coverAudioRef.current) {
      currentAudioRef.current = coverAudioRef.current;
    } else if (currentAudio === 'stego' && stegoAudioRef.current) {
      currentAudioRef.current = stegoAudioRef.current;
    }
  }, [currentAudio]);

  const handleFileUpload = (file, type) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const audioUrl = URL.createObjectURL(file);
      if (type === 'cover') {
        setCoverAudio({ file, url: audioUrl, name: file.name });
      } else if (type === 'secret') {
        setSecretMessage({ file, content: e.target.result, name: file.name });
      } else if (type === 'stego') {
        setStegoAudio({ file, url: audioUrl, name: file.name });
      }
    };
    
    if (type === 'secret') {
      reader.readAsText(file);
    } else {
      reader.readAsDataURL(file);
    }
  };

  const togglePlayback = () => {
    if (currentAudioRef.current) {
      if (isPlaying) {
        currentAudioRef.current.pause();
      } else {
        currentAudioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  

  

  const extractMessage = () => {
    if (!stegoAudio || !stegoKey) {
      alert('Please provide stego audio file and stego key');
      return;
    }

    // Simulasi proses ekstraksi
    setTimeout(() => {
      const extractedText = "This is a secret message that was hidden in the audio file.";
      setExtractedMessage({
        content: extractedText,
        name: fileName || 'extracted_message.txt'
      });
      alert('Message extracted successfully!');
    }, 1500);
  };

  const downloadFile = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Embed Message Tab */}
        {activeTab === 'embed' && (
          <EmbedTab />
        )}

        {/* Extract Message Tab */}
        {activeTab === 'extract' && (
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
                <Unlock className="w-6 h-6 mr-3" />
                Extract Secret Message
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Stego Audio Upload */}
                <div className="space-y-4">
                  <label className="block text-white font-medium">Stego Audio (MP3)</label>
                  <div className="border-2 border-dashed border-white/30 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
                    <input
                      type="file"
                      accept="audio/mp3"
                      onChange={(e) => handleFileUpload(e.target.files[0], 'stego')}
                      className="hidden"
                      id="stego-upload"
                    />
                    <label htmlFor="stego-upload" className="cursor-pointer">
                      <Upload className="w-12 h-12 text-green-300 mx-auto mb-4" />
                      <p className="text-white mb-2">Click to upload stego audio</p>
                      <p className="text-green-200 text-sm">MP3 files with hidden messages</p>
                    </label>
                    {stegoAudio && (
                      <p className="text-green-300 mt-2">✓ {stegoAudio.name}</p>
                    )}
                  </div>
                </div>

                {/* Configuration */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="block text-white font-medium">Stego Key</label>
                    <div className="relative">
                      <input
                        type={showKey ? 'text' : 'password'}
                        value={stegoKey}
                        onChange={(e) => setStegoKey(e.target.value)}
                        className="w-full p-3 bg-white/10 border border-white/30 rounded-lg text-white pr-10"
                        placeholder="Enter extraction key"
                      />
                      <button
                        onClick={() => setShowKey(!showKey)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60"
                      >
                        {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="block text-white font-medium">Output Filename</label>
                    <input
                      type="text"
                      value={fileName}
                      onChange={(e) => setFileName(e.target.value)}
                      className="w-full p-3 bg-white/10 border border-white/30 rounded-lg text-white"
                      placeholder="extracted_message.txt"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={extractMessage}
                className="w-full mt-8 bg-gradient-to-r from-green-500 to-teal-600 text-white py-4 px-8 rounded-xl font-semibold text-lg hover:from-green-600 hover:to-teal-700 transition-all transform hover:scale-105 shadow-lg"
              >
                Extract Message
              </button>
            </div>

            {/* Extracted Message Display */}
            {extractedMessage && (
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-white">Extracted Message</h3>
                  <button
                    onClick={() => downloadFile(extractedMessage.content, extractedMessage.name)}
                    className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <pre className="text-white whitespace-pre-wrap">{extractedMessage.content}</pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AudioSteganographyApp;