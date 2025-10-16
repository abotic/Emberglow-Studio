import React, { useState } from 'react';
import { Trash2, Loader, Video as VideoIcon, Eye, Download, Image as ImageIcon, FileText, Youtube, Clock, HardDrive, X } from 'lucide-react';
import { Video } from '../types';
import { useDownload } from '../hooks/useDownload';
import { api } from '../services/api';
import { VIDEO_TYPE_CONFIG } from '../constants/videoTypes';

interface Props {
  video: Video;
  onDelete: (name: string) => void;
  onViewMetadata: (name: string) => void;
}

export const VideoCard: React.FC<Props> = ({ video, onDelete, onViewMetadata }) => {
  const { downloading, downloadVideo, downloadThumbnail, downloadMetadata } = useDownload();
  const [deleting, setDeleting] = useState(false);

  const videoTypeDisplay = video.duration
    ? video.duration < 61
      ? 'shorts'
      : 'standard'
    : 'standard';

  const handleDelete = async () => {
    if (!confirm(`Delete "${video.display_name}"?`)) return;
    setDeleting(true);
    await onDelete(video.name);
    setDeleting(false);
  };

  const formatDate = (timestamp: number) =>
    new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

  return (
    <div className="group bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl overflow-hidden border border-slate-700/50 hover:border-slate-600/50 transition-all duration-300 shadow-xl">
      <div className="relative">
        {video.status === 'completed' && (
          <>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="absolute top-3 right-3 z-10 bg-red-600/90 hover:bg-red-600 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-all shadow-lg"
            >
              {deleting ? <Loader className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
            </button>
            <div className={`absolute top-3 left-3 z-10 ${VIDEO_TYPE_CONFIG[videoTypeDisplay].color} text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg`}>
              {VIDEO_TYPE_CONFIG[videoTypeDisplay].title}
            </div>
            {video.has_metadata && (
              <div className="absolute bottom-3 right-3 z-10 bg-red-600/90 text-white p-2 rounded-full shadow-lg">
                <Youtube className="w-4 h-4" />
              </div>
            )}
          </>
        )}
        {video.status === 'generating' && (
          <div className="absolute inset-0 bg-gradient-to-br from-blue-900/90 to-cyan-900/90 flex flex-col items-center justify-center z-10">
            <Loader className="w-12 h-12 animate-spin text-blue-400 mb-4" />
            <div className="text-center px-4">
              <div className="text-white font-bold mb-1">Generating...</div>
              <div className="text-blue-300 text-sm">This may take 1-5 minutes</div>
            </div>
          </div>
        )}
        {video.thumbnail ? (
          <img src={api.getVideoUrl(video.thumbnail)} alt={video.name} className="w-full h-48 object-cover" />
        ) : (
          <div className="w-full h-48 bg-slate-700 flex items-center justify-center">
            <VideoIcon className="w-12 h-12 text-slate-500" />
          </div>
        )}
      </div>
      <div className="p-5">
        <h3 className="font-bold text-lg mb-4 line-clamp-2">{video.display_name}</h3>
        <div className="flex justify-between text-xs text-slate-400 mb-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1">
              <HardDrive className="w-3 h-3" />
              <span>{video.size_mb} MB</span>
            </div>
            {video.duration_formatted && (
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{video.duration_formatted}</span>
              </div>
            )}
          </div>
          <span>{formatDate(video.created)}</span>
        </div>
        {video.status === 'completed' ? (
          <div className="space-y-3">
            <a
              href={api.getVideoUrl(video.video!)}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white py-3 px-4 rounded-xl text-sm font-bold transition-all flex items-center justify-center shadow-lg"
            >
              <Eye className="w-4 h-4 mr-2" />
              Watch Video
            </a>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => downloadVideo(video.name)}
                disabled={downloading[`video-${video.name}`]}
                className="bg-green-900/30 hover:bg-green-900/50 border border-green-700/50 text-green-400 py-2 px-3 rounded-xl text-xs transition-all flex items-center justify-center font-medium"
              >
                {downloading[`video-${video.name}`] ? <Loader className="w-3 h-3 animate-spin" /> : <Download className="w-3 h-3" />}
                <span className="ml-1.5 hidden sm:inline">Video</span>
              </button>
              <button
                onClick={() => downloadThumbnail(video.name)}
                disabled={downloading[`thumbnail-${video.name}`]}
                className="bg-orange-900/30 hover:bg-orange-900/50 border border-orange-700/50 text-orange-400 py-2 px-3 rounded-xl text-xs transition-all flex items-center justify-center font-medium"
              >
                {downloading[`thumbnail-${video.name}`] ? <Loader className="w-3 h-3 animate-spin" /> : <ImageIcon className="w-3 h-3" />}
                <span className="ml-1.5 hidden sm:inline">Thumb</span>
              </button>
            </div>
            {video.has_metadata && (
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => onViewMetadata(video.name)}
                  className="bg-red-900/30 hover:bg-red-900/50 border border-red-700/50 text-red-400 py-2 px-3 rounded-xl text-xs transition-all flex items-center justify-center font-medium"
                >
                  <Youtube className="w-3 h-3" />
                  <span className="ml-1.5 hidden sm:inline">View</span>
                </button>
                <button
                  onClick={() => downloadMetadata(video.name)}
                  disabled={downloading[`metadata-${video.name}`]}
                  className="bg-purple-900/30 hover:bg-purple-900/50 border border-purple-700/50 text-purple-400 py-2 px-3 rounded-xl text-xs transition-all flex items-center justify-center font-medium"
                >
                  {downloading[`metadata-${video.name}`] ? <Loader className="w-3 h-3 animate-spin" /> : <FileText className="w-3 h-3" />}
                  <span className="ml-1.5 hidden sm:inline">Get</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="w-full bg-red-900/30 hover:bg-red-900/50 border border-red-700/50 text-red-400 py-2 px-3 rounded-xl text-xs transition-all flex items-center justify-center font-medium"
          >
            {deleting ? <Loader className="w-3 h-3 animate-spin" /> : <X className="w-3 h-3" />}
            <span className="ml-1.5">Cancel</span>
          </button>
        )}
      </div>
    </div>
  );
};