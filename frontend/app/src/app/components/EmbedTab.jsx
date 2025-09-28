'use client';
import React, { useState, useRef, useEffect } from 'react';
import { Upload, Play, Pause, Download, FileAudio, Lock, Unlock, Settings, Calculator, Eye, EyeOff } from 'lucide-react';
import MediaPlayer from './MediaPlayer';
const EmbedTab = ({}) => {
  const [useEncryption, setUseEncryption] = useState(false);
  const [useRandomStart, setUseRandomStart] = useState(false);
  const [nLSB, setNLSB] = useState(1);
  const [psnr, setPsnr] = useState(null);
  const [coverAudio, setCoverAudio] = useState(null);
  const [stegoAudio, setStegoAudio] = useState(null);
  const [secretMessage, setSecretMessage] = useState(null);
  const [showKey, setShowKey] = useState(false);
  const [stegoKey, setStegoKey] = useState('');
  const coverAudioRef = useRef(null);
  const stegoAudioRef = useRef(null);
  
  const embedMessage = () => {
    if (!coverAudio || !secretMessage || !stegoKey) {
      alert('Please provide all required files and stego key');
      return;
    }

    // Simulasi proses embedding
    setTimeout(() => {
      const stegoUrl = coverAudio.url; // Dalam implementasi nyata, ini akan menjadi audio hasil steganografi
      setStegoAudio({
        file: coverAudio.file,
        url: stegoUrl,
        name: `stego_${coverAudio.name}`
      });
      calculatePSNR();
      alert('Message embedded successfully!');
    }, 2000);
  };

  const calculatePSNR = () => {
    // Simulasi perhitungan PSNR
    // Dalam implementasi nyata, ini akan menggunakan data audio yang sesungguhnya
    const simulatedPSNR = 35 + Math.random() * 20;
    setPsnr(simulatedPSNR.toFixed(2));
  };
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
  
  return (
    <div className="space-y-6">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
          <Lock className="w-6 h-6 mr-3" />
          Embed Secret Message
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Cover Audio Upload */}
          <div className="space-y-4">
            <label className="block text-white font-medium">Cover Audio (MP3)</label>
            <div className="border-2 border-dashed border-white/30 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept="audio/mp3"
                onChange={(e) => handleFileUpload(e.target.files[0], 'cover')}
                className="hidden"
                id="cover-upload"
              />
              <label htmlFor="cover-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 text-blue-300 mx-auto mb-4" />
                <p className="text-white mb-2">Click to upload cover audio</p>
                <p className="text-blue-200 text-sm">MP3 files only</p>
              </label>
            </div>
            {coverAudio && <MediaPlayer label="Cover Audio" audio={coverAudio} audioRef={coverAudioRef} />}
          </div>

          {/* Secret Message Upload */}
          <div className="space-y-4">
            <label className="block text-white font-medium">Secret Message File</label>
            <div className="border-2 border-dashed border-white/30 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept=".txt"
                onChange={(e) => handleFileUpload(e.target.files[0], 'secret')}
                className="hidden"
                id="secret-upload"
              />
              <label htmlFor="secret-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 text-purple-300 mx-auto mb-4" />
                <p className="text-white mb-2">Click to upload secret message</p>
                <p className="text-purple-200 text-sm">Text files only</p>
              </label>
              {secretMessage && (
                <p className="text-green-300 mt-2">✓ {secretMessage.name}</p>
              )}
            </div>
          </div>
        </div>

        {/* Configuration Options */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-2">
            <label className="block text-white font-medium">Use Encryption</label>
            <button
              onClick={() => setUseEncryption(!useEncryption)}
              className={`w-full p-3 rounded-lg border transition-colors ${
                useEncryption
                  ? 'bg-green-500/20 border-green-400 text-green-300'
                  : 'bg-white/10 border-white/30 text-white'
              }`}
            >
              {useEncryption ? <Lock className="w-5 h-5 mx-auto" /> : <Unlock className="w-5 h-5 mx-auto" />}
              {useEncryption ? 'Enabled' : 'Disabled'}
            </button>
          </div>

          <div className="space-y-2">
            <label className="block text-white font-medium">Random Start Point</label>
            <button
              onClick={() => setUseRandomStart(!useRandomStart)}
              className={`w-full p-3 rounded-lg border transition-colors ${
                useRandomStart
                  ? 'bg-blue-500/20 border-blue-400 text-blue-300'
                  : 'bg-white/10 border-white/30 text-white'
              }`}
            >
              <Settings className="w-5 h-5 mx-auto" />
              {useRandomStart ? 'Random' : 'Sequential'}
            </button>
          </div>

          <div className="space-y-2">
            <label className="block text-white font-medium">n-LSB</label>
            <select
              value={nLSB}
              onChange={(e) => setNLSB(parseInt(e.target.value))}
              className="w-full p-3 bg-white/10 border border-white/30 rounded-lg text-white"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8].map(n => (
                <option key={n} value={n} className="bg-slate-800">{n} LSB</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-white font-medium">Stego Key</label>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                value={stegoKey}
                onChange={(e) => setStegoKey(e.target.value)}
                className="w-full p-3 bg-white/10 border border-white/30 rounded-lg text-white pr-10"
                placeholder="Enter key"
              />
              <button
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60"
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={embedMessage}
          className="w-full mt-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-4 px-8 rounded-xl font-semibold text-lg hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg"
        >
          Embed Message
        </button>
        {stegoAudio && <MediaPlayer label="Stego Audio" audio={stegoAudio} audioRef={stegoAudioRef} />}
        {<MediaPlayer label="Stego Audio" audio={stegoAudio} audioRef={stegoAudioRef} />}

      </div>

      {/* PSNR Display */}
      {psnr && (
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <Calculator className="w-5 h-5 mr-3" />
            Audio Quality Analysis
          </h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80">Peak Signal-to-Noise Ratio (PSNR)</p>
              <p className="text-3xl font-bold text-white">{psnr} dB</p>
            </div>
            <div className={`px-4 py-2 rounded-full ${
              parseFloat(psnr) >= 30 
                ? 'bg-green-500/20 text-green-300' 
                : 'bg-red-500/20 text-red-300'
            }`}>
              {parseFloat(psnr) >= 30 ? 'Good Quality' : 'Quality Degraded'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmbedTab;
