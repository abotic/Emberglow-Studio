import React from 'react';
import { Loader } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { useProgressPolling } from '../hooks/useProgressPolling';

export const ActiveGenerations: React.FC = () => {
  const { videos } = useApp();
  const generatingVideos = videos.filter(v => v.status === 'generating');
  const progressMap = useProgressPolling(generatingVideos);

  if (generatingVideos.length === 0) return null;

  return (
    <div className="mb-12 space-y-4">
      <h3 className="text-2xl font-bold text-blue-400">Active Generations</h3>
      {generatingVideos.map((video) => {
        if (!video.progress_id) return null;
        
        const progress = progressMap.get(video.progress_id);
        const percentage = progress?.percentage || 0;
        const videoTypeColor = video.video_type === 'shorts' 
          ? 'bg-gradient-to-br from-red-600 to-pink-600'
          : 'bg-gradient-to-br from-blue-600 to-cyan-600';

        return (
          <div key={video.name} className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-5 border border-slate-700/50 shadow-xl">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <div className={`p-2 ${videoTypeColor} rounded-lg shadow-lg`}>
                    <Loader className="w-4 h-4 animate-spin" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white text-base line-clamp-1">{video.display_name}</h4>
                    <p className="text-sm text-slate-400">{progress?.step || 'Initializing'}</p>
                  </div>
                </div>
              </div>
              <span className={`${videoTypeColor} text-white px-2 py-1 rounded-lg text-sm font-bold`}>
                {video.video_type === 'shorts' ? 'SHORT' : 'STANDARD'}
              </span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                className={`${videoTypeColor} h-2 rounded-full transition-all duration-500`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-slate-500">{percentage}% Complete</span>
              {progress?.details && (
                <span className="text-sm text-slate-500">{progress.details}</span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};