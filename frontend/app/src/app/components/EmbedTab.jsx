'use client';
import React, { useState, useRef, useEffect } from 'react';
import { Upload, Play, Pause, Download, FileAudio, Lock, Unlock, Settings, Calculator, Eye, EyeOff } from 'lucide-react';
import MediaPlayer from './MediaPlayer';
const EmbedTab = ({ embedState, setEmbedState }) => {
  const { useEncryption, useRandomStart, nLSB, psnr, coverAudio, stegoAudio, secretMessage, showKey, stegoKey } = embedState;

  const updateState = (updates) => setEmbedState((prev) => ({ ...prev, ...updates }));

  const coverAudioRef = useRef(null);
  const stegoAudioRef = useRef(null);
  const [loading, setLoading] = useState(false);

  const embedMessage = async () => {
    if (!coverAudio || !secretMessage || !stegoKey) {
      alert("Please provide all required files and stego key");
      return;
    }

    const formData = new FormData();
    formData.append("cover_file", coverAudio.file);
    formData.append("secret_file", secretMessage.file);
    formData.append("stego_key", stegoKey);
    formData.append("n_lsb", nLSB);
    formData.append("use_encryption", useEncryption);
    formData.append("use_random", useRandomStart);

    try {
      setLoading(true);
      const res = await fetch("http://localhost:8000/embed", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (!data.success) {
        alert("Embedding failed: " + data.error);
        return;
      }

      const stegoUrl = `http://localhost:8000/${data.embed_file}`;
      updateState({ stegoAudio: { url: stegoUrl, name: data.embed_file.split("/").pop() } });

      updateState({ psnr: data.psnr_score?.toFixed(2) });
      alert("Message embedded successfully!");
    } catch (err) {
      console.error(err);
      alert("Embedding request failed");
    } finally{
      setLoading(false);
    }
  };


  const handleFileUpload = (file, type) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const audioUrl = URL.createObjectURL(file);
      if (type === 'cover') {
        updateState ({ coverAudio: ({ file, url: audioUrl, name: file.name })});
      } else if (type === 'secret') {
        updateState ({ secretMessage: ({ file, content: e.target.result, name: file.name })});
      } else if (type === 'stego') {
        updateState ({ stegoAudio: ({ file, url: audioUrl, name: file.name })});
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
                accept="*/*"
                onChange={(e) => handleFileUpload(e.target.files[0], 'secret')}
                className="hidden"
                id="secret-upload"
              />
              <label htmlFor="secret-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 text-purple-300 mx-auto mb-4" />
                <p className="text-white mb-2">Click to upload secret file</p>
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
              onClick={() => updateState({ useEncryption: !useEncryption })}
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
              onClick={() => updateState({ useRandomStart: (!useRandomStart)})}
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
              onChange={(e) => updateState({ nLSB: parseInt(e.target.value) })}
              className="w-full p-3 bg-white/10 border border-white/30 rounded-lg text-white"
            >
              {[1, 2, 3, 4].map(n => (
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
                onChange={(e) => updateState({ stegoKey: e.target.value })}
                className="w-full p-3 bg-white/10 border border-white/30 rounded-lg text-white pr-10"
                placeholder="Enter key"
              />
              <button
                onClick={() => updateState({ showKey: (!showKey)})}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60"
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        <button
          onClick={embedMessage}
          disabled={loading}
          className={`w-full mt-8 py-4 px-8 rounded-xl font-semibold text-lg shadow-lg transition-all transform ${
            loading
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 hover:scale-105"
          }`}
        >
          {loading ? "Embedding..." : "Embed Message"}
        </button>
        {stegoAudio && (
          <div className="flex flex-col items-center gap-2">
            <MediaPlayer label="Stego Audio" audio={stegoAudio} audioRef={stegoAudioRef} />
            
            {/* Download button */}
            <a
              href={stegoAudio.url}
              download={stegoAudio.name || "stego_audio.wav"}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
            >
              Download Stego Audio
            </a>
          </div>
        )}
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
