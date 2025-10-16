import React, { useState, useEffect } from 'react';
import { Notification } from './Notification';
import { UsageCards } from './UsageCards';
import { VideoTypeSelector } from './VideoTypeSelector';
import { VisualModeSelector } from './VisualModeSelector';
import { ContentModeSelector } from './ContentModeSelector';
import { CategorySelector } from './CategorySelector';
import { TopicSelector } from './TopicSelector';
import { GenerationPanel } from './GenerationPanel';
import { VideoLibrary } from './VideoLibrary';
import { ActiveGenerations } from './ActiveGenerations';
import { useVideoGeneration } from '../hooks/useVideoGeneration';
import { VideoType, VisualMode, VideoCategory } from '../types';
import { VIDEO_TYPE_CONFIG } from '../constants/videoTypes';


export const Dashboard: React.FC = () => {
  const [videoType, setVideoType] = useState<VideoType>('shorts');
  const [visualMode, setVisualMode] = useState<VisualMode>('stability');
  const [selectedCategory, setSelectedCategory] = useState<VideoCategory>('what_if');
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [customTopic, setCustomTopic] = useState('');
  const [useCustomTopic, setUseCustomTopic] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState("21m00Tcm4TlvDq8ikWAM");
  const [stylePreset, setStylePreset] = useState('cinematic');

  const { startGeneration } = useVideoGeneration();

  useEffect(() => {
    const availableCategories = VIDEO_TYPE_CONFIG[videoType].categories;
    if (!availableCategories.includes(selectedCategory)) {
      setSelectedCategory(availableCategories[0]);
    }
    setSelectedTopic(null);
    setCustomTopic('');
    setUseCustomTopic(false);
  }, [videoType, selectedCategory]);

  const handleGenerate = async () => {
    const topicToUse = useCustomTopic ? customTopic.trim() : selectedTopic;
    const categoryToUse = useCustomTopic ? 'custom' : selectedCategory;
    if (!topicToUse) return;

    await startGeneration(
      topicToUse,
      categoryToUse,
      selectedVoice,
      videoType,
      visualMode,
      stylePreset
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8 sm:mb-12">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black mb-4 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Emberglow Studio
          </h1>
          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto">
            Your niche videos? Ready in minutes!
          </p>
        </div>

        <Notification />
        <UsageCards />
        <VideoTypeSelector value={videoType} onChange={setVideoType} />
        <VisualModeSelector value={visualMode} onChange={setVisualMode} />
        <ContentModeSelector useCustomTopic={useCustomTopic} onChange={setUseCustomTopic} />

        {!useCustomTopic && (
          <CategorySelector
            selectedCategory={selectedCategory}
            availableCategories={VIDEO_TYPE_CONFIG[videoType].categories}
            onChange={setSelectedCategory}
          />
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-12">
          <TopicSelector
            useCustomTopic={useCustomTopic}
            customTopic={customTopic}
            setCustomTopic={setCustomTopic}
            selectedTopic={selectedTopic}
            setSelectedTopic={setSelectedTopic}
            selectedCategory={selectedCategory}
            generating={false}
          />

          <GenerationPanel
            selectedTopic={selectedTopic}
            customTopic={customTopic}
            useCustomTopic={useCustomTopic}
            videoType={videoType}
            category={selectedCategory}
            visualMode={visualMode}
            selectedVoice={selectedVoice}
            setSelectedVoice={setSelectedVoice}
            stylePreset={stylePreset}
            setStylePreset={setStylePreset}
            onGenerate={handleGenerate}
          />
        </div>

        <ActiveGenerations />
        <VideoLibrary />
      </div>
    </div>
  );
};