import React from 'react';
import { Edit3 } from 'lucide-react';

interface Props {
  useCustomTopic: boolean;
  onChange: (useCustom: boolean) => void;
}

export const ContentModeSelector: React.FC<Props> = ({ useCustomTopic, onChange }) => {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl mb-8">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-orange-600 to-red-600 rounded-xl shadow-lg">
          <Edit3 className="w-5 h-5" />
        </div>
        <h2 className="text-2xl font-bold">Step 3: Choose Content Mode</h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          onClick={() => onChange(false)}
          className={`border-2 rounded-xl p-5 transition-all duration-300 text-left ${
            !useCustomTopic
              ? 'bg-gradient-to-br from-blue-600 to-cyan-600 border-white/30 shadow-lg scale-105'
              : 'border-slate-600 hover:border-slate-500 bg-slate-800/50 hover:scale-102'
          }`}
        >
          <div className="text-2xl mb-3">📚</div>
          <div className="text-xl font-bold mb-2">Curated Topics</div>
          <div className="text-sm text-slate-300">Choose from expertly crafted topic collections</div>
        </button>
        <button
          onClick={() => onChange(true)}
          className={`border-2 rounded-xl p-5 transition-all duration-300 text-left ${
            useCustomTopic
              ? 'bg-gradient-to-br from-green-600 to-emerald-600 border-white/30 shadow-lg scale-105'
              : 'border-slate-600 hover:border-slate-500 bg-slate-800/50 hover:scale-102'
          }`}
        >
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-2xl">✏️</span>
            <span className="bg-green-500 text-xs px-2 py-1 rounded-full font-bold">BETA</span>
          </div>
          <div className="text-xl font-bold mb-2">Custom Topic</div>
          <div className="text-sm text-slate-300">Create videos on any topic you imagine</div>
        </button>
      </div>
    </div>
  );
};