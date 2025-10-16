import React from 'react';
import { Sparkles } from 'lucide-react';
import { VisualMode } from '../types';
import { VISUAL_MODE_CONFIG } from '../constants/visualModes';

interface Props {
  value: VisualMode;
  onChange: (mode: VisualMode) => void;
}

export const VisualModeSelector: React.FC<Props> = ({ value, onChange }) => {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl mb-8">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-3 bg-gradient-to-br from-yellow-600 to-orange-600 rounded-xl shadow-lg">
          <Sparkles className="w-5 h-5" />
        </div>
        <h2 className="text-2xl font-bold">Step 2: Choose Visuals Source</h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {(Object.keys(VISUAL_MODE_CONFIG) as VisualMode[]).map((mode) => {
          const config = VISUAL_MODE_CONFIG[mode];
          const isSelected = value === mode;

          return (
            <button
              key={mode}
              onClick={() => onChange(mode)}
              className={`border-2 rounded-xl p-5 transition-all duration-300 text-left ${
                isSelected
                  ? `${config.color} border-white/30 shadow-lg scale-105`
                  : 'border-slate-600 hover:border-slate-500 bg-slate-800/50 hover:scale-102'
              }`}
            >
              <div className="text-2xl mb-3">{config.icon}</div>
              <div className="text-xl font-bold mb-2">{config.title}</div>
              <div className="text-sm text-slate-300 mb-3">{config.description}</div>
              <div className="text-xs text-slate-400 bg-slate-900/50 rounded-lg p-2">
                {config.details}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};