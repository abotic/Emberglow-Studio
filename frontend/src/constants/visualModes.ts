import { VisualMode } from "../types";

interface VisualModeConfig {
  title: string;
  description: string;
  icon: string;
  color: string;
  details: string;
}

export const VISUAL_MODE_CONFIG: Record<VisualMode, VisualModeConfig> = {
  stability: {
    title: "AI Images",
    description: "AI-generated custom visuals using the best quality",
    icon: "✨",
    color: "bg-gradient-to-br from-purple-600 to-pink-600",
    details: "Creates unique, high-quality images for your content using advanced AI"
  },
  stock: {
    title: "Stock Media",
    description: "Copyright-free videos & photos crawled from several sources",
    icon: "📸",
    color: "bg-gradient-to-br from-blue-600 to-cyan-600",
    details: "Licensed professional content - mix of HD videos and images"
  }
} as const;

export const VISUAL_MODES: VisualMode[] = ['stability', 'stock'];

interface StylePreset {
  value: string;
  label: string;
}

export const STYLE_PRESETS: readonly StylePreset[] = [
  { value: "cinematic", label: "Cinematic" },
  { value: "photographic", label: "Photographic" },
  { value: "anime", label: "Anime" },
  { value: "fantasy-art", label: "Fantasy Art" },
  { value: "digital-art", label: "Digital Art" },
  { value: "comic-book", label: "Comic Book" },
  { value: "analog-film", label: "Analog Film" },
  { value: "3d-model", label: "3D Model" },
  { value: "line-art", label: "Line Art" },
  { value: "low-poly", label: "Low Poly" },
  { value: "neon-punk", label: "Neon Punk" }
] as const;