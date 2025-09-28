'use client';
import React from 'react';

const ExtractTab = ({
  stegoAudio,
  handleFileUpload,
  stegoKey,
  setStegoKey,
  showKey,
  setShowKey,
  fileName,
  setFileName,
  extractMessage,
  extractedMessage,
  downloadFile,
}) => {
  return (
    <div className="p-6 space-y-4 rounded-2xl shadow-lg bg-slate-800/60 border border-slate-700">
      <h2 className="text-2xl font-semibold text-white">Extract Message</h2>

      {/* Stego Audio Upload */}
      <input
        type="file"
        accept="audio/*"
        onChange={(e) =>
          e.target.files && handleFileUpload(e.target.files[0], 'stego')
        }
        className="w-full text-white"
      />

      {/* Stego Key */}
      <label className="text-white">
        Stego Key:
        <input
          type={showKey ? 'text' : 'password'}
          value={stegoKey}
          onChange={(e) => setStegoKey(e.target.value)}
          className="ml-2 p-1 text-black rounded"
        />
        <button
          type="button"
          onClick={() => setShowKey(!showKey)}
          className="ml-2 text-blue-400 hover:underline"
        >
          {showKey ? 'Hide' : 'Show'}
        </button>
      </label>

      {/* Output file name */}
      <label className="text-white">
        Output File Name:
        <input
          type="text"
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          className="ml-2 p-1 text-black rounded"
        />
      </label>

      {/* Extract button */}
      <button onClick={extractMessage}>Extract Message</button>

      {/* Extracted Message */}
      {extractedMessage && (
        <div className="mt-4 text-white">
          <h3 className="font-semibold">Extracted Message:</h3>
          <pre className="bg-slate-900 p-2 rounded">{extractedMessage}</pre>
          <button onClick={downloadFile} className="mt-2">
            Download as .txt
          </button>
        </div>
      )}
    </div>
  );
};

export default ExtractTab;
