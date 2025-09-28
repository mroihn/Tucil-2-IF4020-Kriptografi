'use client';
import { FileAudio } from 'lucide-react';

const Header = ({ activeTab, setActiveTab }) => {
  return (
    <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <FileAudio className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AudioStego</h1>
                <p className="text-blue-200 text-sm">Audio Steganography Tool</p>
              </div>
            </div>
            
            {/* Tab Navigation */}
            <nav className="flex bg-white/10 rounded-xl p-1">
              <button
                onClick={() => setActiveTab('embed')}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  activeTab === 'embed'
                    ? 'bg-white text-blue-900 shadow-lg'
                    : 'text-white hover:bg-white/20'
                }`}
              >
                Embed Message
              </button>
              <button
                onClick={() => setActiveTab('extract')}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${
                  activeTab === 'extract'
                    ? 'bg-white text-blue-900 shadow-lg'
                    : 'text-white hover:bg-white/20'
                }`}
              >
                Extract Message
              </button>
            </nav>
          </div>
        </div>
      </header>
  );
};

export default Header;
