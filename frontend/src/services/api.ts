import {
  TopicsData,
  Voice,
  GenerationProgress,
  Video,
  VideoMetadata,
  ElevenLabsUsage,
  OpenAIUsage,
  StorageUsage,
  GenerateVideoRequest
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || '';

class ApiService {
  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, options);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  async getTopics(): Promise<TopicsData> {
    return this.fetch<TopicsData>('/api/topics');
  }

  async getVoices(): Promise<{ voices: Voice[] }> {
    return this.fetch<{ voices: Voice[] }>('/api/voices');
  }

  async testVoice(voiceId: string, videoType: string): Promise<{ audio_base64: string }> {
    return this.fetch('/api/test-voice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ voice_id: voiceId, video_type: videoType })
    });
  }

  async generateVideo(request: GenerateVideoRequest): Promise<{ progress_id: string; video_type: string }> {
    return this.fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
  }

  async getProgress(progressId: string): Promise<GenerationProgress> {
    return this.fetch<GenerationProgress>(`/api/progress/${progressId}`);
  }

  async getVideos(): Promise<Video[]> {
    return this.fetch<Video[]>('/api/videos');
  }

  async deleteVideo(videoName: string): Promise<{ message: string }> {
    return this.fetch(`/api/videos/${videoName}`, { method: 'DELETE' });
  }

  async getMetadata(videoName: string): Promise<VideoMetadata> {
    return this.fetch<VideoMetadata>(`/api/metadata/${videoName}`);
  }

  async getElevenLabsUsage(): Promise<ElevenLabsUsage> {
    return this.fetch<ElevenLabsUsage>('/api/elevenlabs/usage');
  }

  async getOpenAIUsage(): Promise<OpenAIUsage> {
    return this.fetch<OpenAIUsage>('/api/openai/usage');
  }

  async getStorageUsage(): Promise<StorageUsage> {
    return this.fetch<StorageUsage>('/api/storage/usage');
  }

  getDownloadUrl(type: 'video' | 'thumbnail' | 'metadata', videoName: string): string {
    return `${API_URL}/api/download/${type}/${videoName}`;
  }

  getVideoUrl(videoPath: string): string {
    return `${API_URL}${videoPath}`;
  }
}

export const api = new ApiService();