import React from 'react';
import { Film } from 'lucide-react';
import { VideoType } from '../types';
import { VIDEO_TYPE_CONFIG } from '../constants/videoTypes';

interface Props {
  value: VideoType;
  onChange: (type: VideoType) => void;
}

export const VideoTypeSelector: React.FC<Props> = ({ value, onChange }) => {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl mb-8">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-pink-600 to-rose-600 rounded-xl shadow-lg">
          <Film className="w-5 h-5" />
        </div>
        <h2 className="text-2xl font-bold">Step 1: Choose Video Format</h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {(Object.keys(VIDEO_TYPE_CONFIG) as VideoType[]).map((type) => {
          const config = VIDEO_TYPE_CONFIG[type];
          const Icon = config.icon;
          const isSelected = value === type;
          const isDisabled = !config.enabled;

          return (
            <button
              key={type}
              onClick={() => !isDisabled && onChange(type)}
              disabled={isDisabled}
              className={`relative border-2 rounded-xl p-5 transition-all duration-300 text-left ${isSelected
                  ? `${config.color} border-white/30 shadow-lg scale-105`
                  : isDisabled
                    ? 'border-slate-700 bg-slate-800/30 opacity-50 cursor-not-allowed'
                    : 'border-slate-600 hover:border-slate-500 bg-slate-800/50 hover:scale-102'
                }`}
            >

              <div className="flex items-center justify-between mb-3">
                <div className="text-xl font-bold">{config.title}</div>
                <Icon className="w-6 h-6" />
              </div>
              <div className="text-sm text-slate-300 mb-3">{config.description}</div>
              <div className="bg-slate-900/50 text-xs text-slate-400 px-3 py-1.5 rounded-lg inline-block font-medium">
                {config.duration}
              </div>
              {isDisabled && config.betaContact && (
                <>
                  <div className="mt-3 text-xs text-purple-400">
                    Contact: {config.betaContact}
                  </div>
                  <div className="absolute bottom-4 right-2">
                    <span className="bg-purple-600 text-xs px-2 py-1 rounded-full font-medium">BETA</span>
                  </div>
                </>

              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};