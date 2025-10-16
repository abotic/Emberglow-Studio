import { useEffect, useState, useRef } from 'react';
import { useApp } from '../contexts/AppContext';
import { api } from '../services/api';
import { GenerationProgress, Video } from '../types';

export const useProgressPolling = (generatingVideos: Video[]) => {
  const { refreshVideos, showNotification } = useApp();
  const [progressMap, setProgressMap] = useState<Map<string, GenerationProgress>>(new Map());

  const notifiedCompletionsRef = useRef<Set<string>>(new Set());
  const refreshScheduledRef = useRef<Set<string>>(new Set());
  const missingCountRef = useRef<Map<string, number>>(new Map());

  useEffect(() => {
    if (generatingVideos.length === 0) {
      setProgressMap(new Map());
      notifiedCompletionsRef.current.clear();
      refreshScheduledRef.current.clear();
      missingCountRef.current.clear();
      return;
    }

    let isPolling = true;

    const pollProgress = async () => {
      if (!isPolling) return;
      
      for (const video of generatingVideos) {
        if (!video.progress_id) continue;

        try {
          const progress = await api.getProgress(video.progress_id);
          const existing = progressMap.get(video.progress_id);
          
          if (progress.status === 'waiting' && progress.percentage === 0 && existing && existing.percentage > 0) {
            const count = (missingCountRef.current.get(video.progress_id) || 0) + 1;
            missingCountRef.current.set(video.progress_id, count);
            
            if (count >= 2 && !refreshScheduledRef.current.has(video.progress_id)) {
              console.log(`Progress lost for ${video.display_name}, refreshing video list`);
              refreshScheduledRef.current.add(video.progress_id);
              refreshVideos();
            }
            continue;
          }
          
          missingCountRef.current.delete(video.progress_id);
          
          if (progress.status === 'completed' && progress.percentage === 100) {
            if (!notifiedCompletionsRef.current.has(video.progress_id)) {
              notifiedCompletionsRef.current.add(video.progress_id);
              showNotification(`Video completed: "${video.display_name}"`, 'success');
              
              setTimeout(() => {
                if (isPolling) {
                  refreshVideos();
                  refreshScheduledRef.current.delete(video.progress_id!);
                  notifiedCompletionsRef.current.delete(video.progress_id!);
                  missingCountRef.current.delete(video.progress_id!);
                }
              }, 2000);
            }
          } else if (progress.status === 'error') {
            if (!notifiedCompletionsRef.current.has(video.progress_id)) {
              notifiedCompletionsRef.current.add(video.progress_id);
              showNotification(`Generation failed: "${video.display_name}"`, 'error');
              setTimeout(() => {
                if (isPolling) {
                  refreshVideos();
                  notifiedCompletionsRef.current.delete(video.progress_id!);
                  missingCountRef.current.delete(video.progress_id!);
                }
              }, 1000);
            }
          }
          
          if (progress.percentage > (existing?.percentage || -1)) {
            setProgressMap(prev => {
              const newMap = new Map(prev);
              newMap.set(video.progress_id!, progress);
              return newMap;
            });
          }
        } catch (error) {
          console.error('Error polling progress:', error);
        }
      }
    };

    pollProgress();
    const interval = setInterval(pollProgress, 3000);

    return () => {
      isPolling = false;
      clearInterval(interval);
    };
  }, [generatingVideos.map(v => v.progress_id).join(',')]);

  return progressMap;
};