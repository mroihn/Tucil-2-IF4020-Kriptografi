import { useState } from 'react';

export const useFileHandler = () => {
  const [coverAudio, setCoverAudio] = useState(null);
  const [secretMessage, setSecretMessage] = useState(null);
  const [stegoAudio, setStegoAudio] = useState(null);

  const handleFileUpload = (file, type) => {
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const audioUrl = URL.createObjectURL(file);
      if (type === 'cover') {
        setCoverAudio({ file, url: audioUrl, name: file.name });
      } else if (type === 'secret') {
        setSecretMessage({ file, content: e.target?.result, name: file.name });
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

  const downloadFile = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const clearFiles = () => {
    setCoverAudio(null);
    setSecretMessage(null);
    setStegoAudio(null);
  };

  return {
    coverAudio,
    secretMessage,
    stegoAudio,
    handleFileUpload,
    downloadFile,
    clearFiles,
    setCoverAudio,
    setSecretMessage,
    setStegoAudio
  };
};