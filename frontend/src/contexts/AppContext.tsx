import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '../services/api';
import {
  TopicsData,
  Voice,
  Video,
  ElevenLabsUsage,
  OpenAIUsage,
  StorageUsage,
  Notification
} from '../types';

interface AppContextType {
  topics: TopicsData;
  voices: Voice[];
  videos: Video[];
  elevenLabsUsage: ElevenLabsUsage | null;
  openaiUsage: OpenAIUsage | null;
  storageUsage: StorageUsage | null;
  notification: Notification | null;
  activeGenerations: Map<string, string>;
  showNotification: (message: string, type?: Notification['type']) => void;
  refreshTopics: () => Promise<void>;
  refreshVideos: () => Promise<void>;
  refreshUsage: () => Promise<void>;
  setActiveGeneration: (projectName: string, progressId: string) => void;
  removeActiveGeneration: (projectName: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [topics, setTopics] = useState<TopicsData>({ why: [], what_if: [], hidden_truths: [] });
  const [voices, setVoices] = useState<Voice[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);
  const [elevenLabsUsage, setElevenLabsUsage] = useState<ElevenLabsUsage | null>(null);
  const [openaiUsage, setOpenaiUsage] = useState<OpenAIUsage | null>(null);
  const [storageUsage, setStorageUsage] = useState<StorageUsage | null>(null);
  const [notification, setNotification] = useState<Notification | null>(null);
  const [activeGenerations, setActiveGenerations] = useState<Map<string, string>>(new Map());

  const showNotification = (message: string, type: Notification['type'] = 'success') => {
    setNotification({ message, type });
  };

  const setActiveGeneration = (projectName: string, progressId: string) => {
    setActiveGenerations(prev => new Map(prev).set(projectName, progressId));
  };

  const removeActiveGeneration = (projectName: string) => {
    setActiveGenerations(prev => {
      const next = new Map(prev);
      next.delete(projectName);
      return next;
    });
  };

  const refreshTopics = async () => {
    try {
      const data = await api.getTopics();
      setTopics(data);
    } catch (error) {
      console.error('Error fetching topics:', error);
    }
  };

  const refreshVideos = async () => {
    try {
      const data = await api.getVideos();
      setVideos(data);
    } catch (error) {
      console.error('Error fetching videos:', error);
    }
  };

  const refreshUsage = async () => {
    try {
      const [elevenlabs, openai, storage] = await Promise.all([
        api.getElevenLabsUsage(),
        api.getOpenAIUsage(),
        api.getStorageUsage()
      ]);
      setElevenLabsUsage(elevenlabs);
      setOpenaiUsage(openai);
      setStorageUsage(storage);
    } catch (error) {
      console.error('Error fetching usage:', error);
    }
  };

  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const data = await api.getVoices();
        setVoices(data.voices || []);
      } catch (error) {
        console.error('Error fetching voices:', error);
      }
    };

    refreshTopics();
    refreshVideos();
    refreshUsage();
    fetchVoices();
  }, []);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  return (
    <AppContext.Provider
      value={{
        topics,
        voices,
        videos,
        elevenLabsUsage,
        openaiUsage,
        storageUsage,
        notification,
        activeGenerations,
        showNotification,
        refreshTopics,
        refreshVideos,
        refreshUsage,
        setActiveGeneration,
        removeActiveGeneration
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
};