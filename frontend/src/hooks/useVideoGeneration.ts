import { api } from '../services/api';
import { useApp } from '../contexts/AppContext';
import { VideoType, VideoCategory, VisualMode } from '../types';

export const useVideoGeneration = () => {
  const { showNotification, refreshVideos } = useApp();

  const startGeneration = async (
    topic: string,
    category: VideoCategory,
    voiceId: string,
    videoType: VideoType,
    visualMode: VisualMode,
    stylePreset: string
  ) => {
    if (topic.trim().length < 5) {
      showNotification('Topic must be at least 5 characters', 'error');
      return;
    }

    if (topic.trim().length > 500) {
      showNotification('Topic must be less than 500 characters', 'error');
      return;
    }

    try {
      await api.generateVideo({
        topic: topic.trim(),
        category,
        voice_id: voiceId,
        video_type: videoType,
        generation_mode: visualMode,
        ai_provider: visualMode === 'stock' ? undefined : visualMode,
        style_preset: stylePreset
      });

      showNotification(`🚀 Started generating: "${topic}"`, 'info');
      setTimeout(() => refreshVideos(), 2000);
    } catch (error: any) {
      showNotification(`Failed to start: ${error.message}`, 'error');
    }
  };

  return { startGeneration };
};