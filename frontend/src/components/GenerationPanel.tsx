import React, { useState, useEffect } from 'react';
import { Play, Volume2, Loader } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { api } from '../services/api';
import { VideoType, VideoCategory, VisualMode } from '../types';
import { VIDEO_TYPE_CONFIG } from '../constants/videoTypes';
import { VISUAL_MODE_CONFIG } from '../constants/visualModes';
import { STYLE_PRESETS } from '../constants/visualModes';

interface Props {
  selectedTopic: string | null;
  customTopic: string;
  useCustomTopic: boolean;
  videoType: VideoType;
  category: VideoCategory;
  visualMode: VisualMode;
  selectedVoice: string;
  setSelectedVoice: (voice: string) => void;
  stylePreset: string;
  setStylePreset: (preset: string) => void;
  onGenerate: () => Promise<void>;
}

export const GenerationPanel: React.FC<Props> = ({
  selectedTopic,
  customTopic,
  useCustomTopic,
  videoType,
  category,
  visualMode,
  selectedVoice,
  setSelectedVoice,
  stylePreset,
  setStylePreset,
  onGenerate
}) => {
  const { voices, showNotification, videos } = useApp();
  const [testingVoice, setTestingVoice] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  const topicToUse = useCustomTopic ? customTopic.trim() : selectedTopic;
  
  const normalizeText = (text: string) => {
    return text.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim();
  };

  const isTopicGenerating = () => {
    if (!topicToUse) return false;
    const normalized = normalizeText(topicToUse);
    return videos
      .filter(v => v.status === 'generating')
      .some(v => normalizeText(v.display_name) === normalized);
  };

  useEffect(() => {
    if (isStarting && isTopicGenerating()) {
      setIsStarting(false);
    }
  }, [videos, isStarting, topicToUse]);

  const testVoice = async () => {
    setTestingVoice(true);
    try {
      const data = await api.testVoice(selectedVoice, videoType);
      const audio = new Audio(`data:audio/mp3;base64,${data.audio_base64}`);
      audio.play();
      showNotification('🔊 Voice test played successfully!', 'success');
    } catch (error) {
      showNotification('Failed to test voice', 'error');
    } finally {
      setTestingVoice(false);
    }
  };

  const getRecommendedVoices = () => {
    if (!voices.length) return [];
    return voices.filter(voice =>
      !voice.recommended_for ||
      voice.recommended_for.length === 0 ||
      voice.recommended_for.includes(videoType) ||
      voice.recommended_for.includes(category)
    );
  };

  const handleGenerate = async () => {
    setIsStarting(true);
    try {
      await onGenerate();
    } catch {
      setIsStarting(false);
    }
  };

  const isDisabled = !topicToUse || isStarting || isTopicGenerating();

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl">
      <h2 className="text-2xl font-bold mb-6">Generate Video</h2>

      <div className="mb-6 relative z-20">
        <label className="block text-sm font-medium mb-3 text-slate-300">Narrator Voice:</label>
        <div className="flex gap-3">
          <select
            value={selectedVoice}
            onChange={(e) => setSelectedVoice(e.target.value)}
            style={{width: '100%'}}
            className="flex-1 bg-slate-700/50 text-white rounded-xl px-4 py-3 border-2 border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all h-12"
            disabled={isStarting}
          >
            {getRecommendedVoices().map((voice) => (
              <option key={voice.voice_id} value={voice.voice_id}>
                {voice.name} - {voice.description}
              </option>
            ))}
          </select>
          <button
            onClick={testVoice}
            disabled={testingVoice || !selectedVoice || isStarting}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-slate-700 disabled:to-slate-700 disabled:cursor-not-allowed text-white px-4 rounded-xl transition-all flex items-center justify-center shadow-lg h-12 w-12 flex-shrink-0"
          >
            {testingVoice ? <Loader className="w-5 h-5 animate-spin" /> : <Volume2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {visualMode === 'stability' && (
        <div className="mb-6 relative z-10">
          <label className="block text-sm font-medium mb-3 text-slate-300">Image Style:</label>
          <select
            value={stylePreset}
            onChange={(e) => setStylePreset(e.target.value)}
            className="w-full bg-slate-700/50 text-white rounded-xl px-4 py-3 border-2 border-slate-600 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all h-12"
            disabled={isStarting}
          >
            {STYLE_PRESETS.map(preset => (
              <option key={preset.value} value={preset.value}>{preset.label}</option>
            ))}
          </select>
        </div>
      )}

      {topicToUse && (
        <div className="mb-6 p-4 bg-slate-700/30 rounded-xl border border-slate-600/30">
          <h3 className="text-sm font-semibold mb-2 text-slate-300">Selected Topic:</h3>
          <p className="text-white text-sm mb-3 break-words">{topicToUse}</p>
          <div className="flex flex-wrap gap-2 text-xs">
            <span className={`${VIDEO_TYPE_CONFIG[videoType].color} text-white px-3 py-1 rounded-full font-medium shadow-lg`}>
              {VIDEO_TYPE_CONFIG[videoType].title}
            </span>
            <span className="bg-gradient-to-r from-blue-900/50 to-cyan-900/50 text-blue-300 px-3 py-1 rounded-full font-medium border border-blue-700/30">
              {VISUAL_MODE_CONFIG[visualMode].title}
            </span>
          </div>
        </div>
      )}

      <button
        onClick={handleGenerate}
        disabled={isDisabled}
        className={`w-full py-4 px-6 rounded-xl font-bold text-lg transition-all duration-300 flex items-center justify-center space-x-3 ${
          !isDisabled
            ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-xl hover:scale-105'
            : 'bg-slate-700 cursor-not-allowed opacity-50'
        }`}
      >
        {isStarting ? (
          <>
            <Loader className="w-6 h-6 animate-spin" />
            <span>Starting...</span>
          </>
        ) : (
          <>
            <Play className="w-6 h-6" />
            <span>Generate {VIDEO_TYPE_CONFIG[videoType].title}</span>
          </>
        )}
      </button>
    </div>
  );
};