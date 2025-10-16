import { VideoCategory } from "../types";

interface CategoryConfig {
  title: string;
  description: string;
  color: string;
  icon: string;
  accent: string;
}

export const CATEGORY_CONFIG: Record<VideoCategory, CategoryConfig> = {
    what_if: {
    title: "What If...?",
    description: "Mind-bending hypothetical scenarios",
    color: "bg-gradient-to-br from-blue-600 to-cyan-600",
    icon: "🌍",
    accent: "blue"
  },
  why: {
    title: "Why Does This Happen?",
    description: "Everyday mysteries, weird biology, brain quirks",
    color: "bg-gradient-to-br from-purple-600 to-pink-600",
    icon: "🧠",
    accent: "purple"
  },
  hidden_truths: {
    title: "Hidden Truths",
    description: "Dark secrets behind systems we live in",
    color: "bg-gradient-to-br from-red-600 to-orange-600",
    icon: "💰",
    accent: "red"
  },
  custom: {
    title: "Custom Topic",
    description: "Write your own topic - experimental feature",
    color: "bg-gradient-to-br from-green-600 to-emerald-600",
    icon: "✏️",
    accent: "green"
  }
} as const;

export const CATEGORIES: VideoCategory[] = ['what_if', 'why', 'hidden_truths', 'custom'];