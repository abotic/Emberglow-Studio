import React, { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { VideoCard } from './VideoCard';
import { MetadataModal } from './MetadataModal';
import { api } from '../services/api';
import { VideoMetadata } from '../types';

export const VideoLibrary: React.FC = () => {
  const { videos, refreshVideos, refreshTopics, refreshUsage, showNotification } = useApp();
  const [viewingMetadata, setViewingMetadata] = useState<string | null>(null);
  const [metadataContent, setMetadataContent] = useState<VideoMetadata | null>(null);

  const handleDelete = async (videoName: string) => {
    try {
      await api.deleteVideo(videoName);
      showNotification('Video deleted successfully!', 'success');
      await Promise.all([refreshVideos(), refreshTopics(), refreshUsage()]);
    } catch (error) {
      console.error('Error deleting video:', error);
      showNotification('Failed to delete video', 'error');
    }
  };

  const handleViewMetadata = async (videoName: string) => {
    setViewingMetadata(videoName);
    try {
      const data = await api.getMetadata(videoName);
      setMetadataContent(data);
    } catch (error) {
      console.error('Error fetching metadata:', error);
      showNotification('Failed to load metadata', 'error');
      setViewingMetadata(null);
    }
  };

  if (videos.length === 0) return null;

  return (
    <>
      <div className="mt-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Your Video Library
          </h2>
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-5 py-2 rounded-full border border-slate-700/50 shadow-lg">
            <span className="text-slate-300 font-bold">{videos.length} videos</span>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {videos.map((video) => (
            <VideoCard
              key={video.name}
              video={video}
              onDelete={handleDelete}
              onViewMetadata={handleViewMetadata}
            />
          ))}
        </div>
      </div>

      {viewingMetadata && metadataContent && (
        <MetadataModal
          videoName={viewingMetadata}
          metadata={metadataContent}
          onClose={() => {
            setViewingMetadata(null);
            setMetadataContent(null);
          }}
        />
      )}
    </>
  );
};