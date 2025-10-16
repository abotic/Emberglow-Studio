import { Film, Zap, Clock, LucideIcon } from 'lucide-react';
import { VideoCategory, VideoType } from '../types';

interface VideoTypeConfig {
  title: string;
  description: string;
  duration: string;
  icon: LucideIcon;
  color: string;
  accent: string;
  categories: VideoCategory[];
  enabled: boolean;
  betaContact?: string;
}

export const VIDEO_TYPE_CONFIG: Record<VideoType, VideoTypeConfig> = {
  shorts: {
    title: "YouTube Shorts",
    description: "30-60 second viral content",
    duration: "30-60 sec",
    icon: Zap,
    color: "bg-gradient-to-br from-red-600 to-pink-600",
    accent: "red",
    categories: ['what_if', 'why', 'hidden_truths', 'custom'],
    enabled: true
  },
  standard: {
    title: "Standard Video",
    description: "2-4 minute educational content",
    duration: "2-4 min",
    icon: Film,
    color: "bg-gradient-to-br from-blue-600 to-cyan-600",
    accent: "blue",
    categories: ['what_if', 'why', 'hidden_truths', 'custom'],
    enabled: true
  },
  longform: {
    title: "Long-Form Content",
    description: "30 minutes to 5 hours - Contact for Beta Access",
    duration: "30min-5hr",
    icon: Clock,
    color: "bg-gradient-to-br from-purple-600 to-indigo-600",
    accent: "purple",
    categories: [],
    enabled: false,
    betaContact: "abotic00@gmail.com"
  }
} as const;

export const VIDEO_TYPES: VideoType[] = ['shorts', 'standard', 'longform'];