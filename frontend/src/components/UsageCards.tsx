import React from 'react';
import { Volume2, Brain, Database, Loader } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

export const UsageCards: React.FC = () => {
  const { elevenLabsUsage, openaiUsage, storageUsage } = useApp();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl shadow-lg">
              {elevenLabsUsage ? <Volume2 className="w-5 h-5" /> : <Loader className="w-5 h-5 animate-spin" />}
            </div>
            <div>
              <h3 className="font-bold text-lg">Credits Remaining</h3>
            </div>
          </div>
          {elevenLabsUsage && (
            <div className="text-right">
              <p className="text-lg font-bold">{Math.max(0, elevenLabsUsage.character_limit - elevenLabsUsage.character_count).toLocaleString()}</p>
              <p className="text-xs text-slate-400">of {elevenLabsUsage.character_limit.toLocaleString()}</p>
            </div>
          )}
        </div>
        {elevenLabsUsage ? (
          <div className="w-full bg-slate-700/50 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${
                (elevenLabsUsage.character_count / elevenLabsUsage.character_limit) * 100 > 90
                  ? 'bg-gradient-to-r from-red-600 to-red-500'
                  : (elevenLabsUsage.character_count / elevenLabsUsage.character_limit) * 100 > 70
                  ? 'bg-gradient-to-r from-yellow-600 to-yellow-500'
                  : 'bg-gradient-to-r from-green-600 to-green-500'
              }`}
              style={{
                width: `${Math.min((elevenLabsUsage.character_count / elevenLabsUsage.character_limit) * 100, 100)}%`
              }}
            />
          </div>
        ) : (
          <div className="text-sm text-slate-400">Loading...</div>
        )}
      </div>

      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl shadow-lg">
            {openaiUsage ? <Brain className="w-5 h-5" /> : <Loader className="w-5 h-5 animate-spin" />}
          </div>
          <div>
            <h3 className="font-bold text-lg">Integration Status</h3>
            {openaiUsage ? (
              <p className="text-xs text-emerald-400 capitalize font-medium">{openaiUsage.status}</p>
            ) : (
              <p className="text-xs text-slate-400">Loading...</p>
            )}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-green-600 to-emerald-600 rounded-xl shadow-lg">
              {storageUsage ? <Database className="w-5 h-5" /> : <Loader className="w-5 h-5 animate-spin" />}
            </div>
            <div>
              <h3 className="font-bold text-lg">Storage</h3>
              {storageUsage && <p className="text-xs text-slate-400">{storageUsage.video_count} videos</p>}
            </div>
          </div>
          {storageUsage && (
            <div className="text-right">
              <p className="text-lg font-bold">{storageUsage.total_size_gb} GB</p>
              <p className="text-xs text-slate-400">{storageUsage.total_size_mb} MB</p>
            </div>
          )}
        </div>
        {storageUsage?.video_type_counts && (
          <div className="mt-4 flex justify-between text-xs text-slate-400">
            <span>{storageUsage.video_type_counts.shorts || 0} shorts</span>
            <span>{storageUsage.video_type_counts.standard || 0} standard</span>
          </div>
        )}
      </div>
    </div>
  );
};