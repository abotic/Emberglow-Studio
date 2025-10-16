import { useState } from 'react';
import { api } from '../services/api';
import { useApp } from '../contexts/AppContext';

interface DownloadState {
  [key: string]: boolean;
}

export const useDownload = () => {
  const [downloading, setDownloading] = useState<DownloadState>({});
  const { showNotification } = useApp();

  const downloadFile = async (url: string, filename: string, key: string) => {
    setDownloading(prev => ({ ...prev, [key]: true }));
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error(`Error downloading ${filename}:`, error);
      showNotification(`Failed to download ${filename}`, 'error');
    } finally {
      setDownloading(prev => ({ ...prev, [key]: false }));
    }
  };

  const downloadVideo = (videoName: string) => {
    downloadFile(
      api.getDownloadUrl('video', videoName),
      `${videoName}.mp4`,
      `video-${videoName}`
    );
  };

  const downloadThumbnail = (videoName: string) => {
    downloadFile(
      api.getDownloadUrl('thumbnail', videoName),
      `${videoName}_thumbnail.jpg`,
      `thumbnail-${videoName}`
    );
  };

  const downloadMetadata = (videoName: string) => {
    downloadFile(
      api.getDownloadUrl('metadata', videoName),
      `${videoName}_metadata.txt`,
      `metadata-${videoName}`
    );
  };

  return {
    downloading,
    downloadVideo,
    downloadThumbnail,
    downloadMetadata
  };
};