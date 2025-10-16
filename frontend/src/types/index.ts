export type VideoType = 'shorts' | 'standard' | 'longform';
export type VisualMode = 'stability' | 'stock';
export type VideoCategory = 'why' | 'what_if' | 'hidden_truths' | 'custom';
export type NotificationType = 'success' | 'error' | 'info';

export interface Topic {
  title: string;
  completed: boolean;
}

export interface TopicsData {
  why: Topic[];
  what_if: Topic[];
  hidden_truths: Topic[];
}

export interface Voice {
  voice_id: string;
  name: string;
  category: string;
  description: string;
  recommended_for: string[];
}

export interface GenerationProgress {
  step: string;
  percentage: number;
  status: 'processing' | 'completed' | 'error' | 'waiting';
  topic?: string;
  video_type?: VideoType;
  details?: string;
}

export interface Video {
  name: string;
  display_name: string;
  video: string | null;
  thumbnail: string | null;
  size_mb: number;
  duration: number | null;
  duration_formatted: string | null;
  created: number;
  status: 'completed' | 'generating';
  has_metadata: boolean;
  progress_id?: string;
  video_type?: string;
}

export interface VideoMetadata {
  title: string;
  description: string;
  tags: string[];
  timestamps?: string[];
  video_type: VideoType;
  original_topic?: string;
}

export interface ElevenLabsUsage {
  character_count: number;
  character_limit: number;
  tier: string;
  status: string;
}

export interface OpenAIUsage {
  status: string;
  current_month: string;
  note?: string;
}

export interface StorageUsage {
  total_size_bytes: number;
  total_size_mb: number;
  total_size_gb: number;
  video_count: number;
  video_type_counts: {
    standard: number;
    shorts: number;
  };
  projects: any[];
}

export interface Notification {
  message: string;
  type: NotificationType;
}

export interface GenerateVideoRequest {
  topic: string;
  category: VideoCategory;
  voice_id: string;
  video_type: VideoType;
  generation_mode: VisualMode;
  ai_provider?: string;
  style_preset: string;
}