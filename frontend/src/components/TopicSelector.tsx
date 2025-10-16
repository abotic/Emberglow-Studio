import React from 'react';
import { CheckCircle, Loader } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { VideoCategory, Topic } from '../types';
import { CATEGORY_CONFIG } from '../constants/categories';


interface Props {
  useCustomTopic: boolean;
  customTopic: string;
  setCustomTopic: (topic: string) => void;
  selectedTopic: string | null;
  setSelectedTopic: (topic: string | null) => void;
  selectedCategory: VideoCategory;
  generating: boolean;
}


const MAX_TOPIC_LENGTH = 500;


export const TopicSelector: React.FC<Props> = ({
  useCustomTopic,
  customTopic,
  setCustomTopic,
  selectedTopic,
  setSelectedTopic,
  selectedCategory,
  generating
}) => {
  const { topics, showNotification, videos } = useApp();

  const categoryTopics: Topic[] = selectedCategory !== 'custom' ? (topics[selectedCategory] || []) : [];
  
  const generatingTopics = videos
    .filter(v => v.status === 'generating')
    .map(v => v.display_name.toLowerCase());

  const completedVideos = videos
    .filter(v => v.status === 'completed')
    .map(v => v.display_name.toLowerCase());

  const handleCustomTopicChange = (value: string) => {
    if (value.length > MAX_TOPIC_LENGTH) {
      showNotification(`Topic too long (max ${MAX_TOPIC_LENGTH} characters)`, 'error');
      return;
    }
    setCustomTopic(value);
  };

  const normalizeText = (text: string) => {
    return text.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim();
  };

  const isTopicGenerating = (topic: string) => {
    const normalized = normalizeText(topic);
    return generatingTopics.some(gt => normalizeText(gt) === normalized);
  };

  const isTopicCompleted = (topic: string) => {
    const normalized = normalizeText(topic);
    return completedVideos.some(cv => normalizeText(cv) === normalized);
  };

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 shadow-xl">
      <h2 className="text-2xl font-bold mb-6">
        {useCustomTopic ? 'Create Custom Topic' : 'Select Topic'}
      </h2>
      {useCustomTopic ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3 text-slate-300">
              Describe your video topic:
            </label>
            <textarea
              value={customTopic}
              onChange={(e) => handleCustomTopicChange(e.target.value)}
              placeholder="e.g., Why is the sky blue?"
              className="w-full bg-slate-700/50 text-white rounded-xl p-4 border-2 border-slate-600 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 resize-none transition-all duration-300 min-h-[150px]"
              rows={6}
              disabled={generating}
              maxLength={MAX_TOPIC_LENGTH}
            />
            <div className="text-xs text-slate-400 mt-1 text-right">
              {customTopic.length} / {MAX_TOPIC_LENGTH}
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-900/20 to-cyan-900/20 border border-blue-700/30 rounded-xl p-4">
            <div className="text-sm text-blue-300">
              <strong>✨ AI-Powered Creation:</strong> Our advanced AI will craft an engaging script
              and find the perfect visuals to bring your idea to life.
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
          {categoryTopics.map((topic: Topic, idx: number) => {
            const isGenerating = isTopicGenerating(topic.title);
            const isCompleted = topic.completed || isTopicCompleted(topic.title);
            const isDisabled = isCompleted || isGenerating;
            
            return (
              <button
                key={idx}
                onClick={() => !isDisabled && setSelectedTopic(topic.title)}
                disabled={isDisabled}
                className={`w-full p-4 rounded-xl transition-all duration-300 text-left border-2 ${
                  isDisabled
                    ? 'bg-slate-700/30 opacity-50 cursor-not-allowed border-slate-600/50'
                    : selectedTopic === topic.title
                    ? `${CATEGORY_CONFIG[selectedCategory].color} border-white/30 shadow-lg`
                    : 'bg-slate-700/50 hover:bg-slate-600/50 border-slate-600/30 hover:border-slate-500/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{topic.title}</span>
                  {isCompleted && (
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5 text-emerald-500" />
                      <span className="text-xs text-emerald-400 bg-emerald-900/30 px-2 py-1 rounded-lg font-medium">
                        Completed
                      </span>
                    </div>
                  )}
                  {isGenerating && (
                    <div className="flex items-center space-x-2">
                      <Loader className="w-5 h-5 text-blue-500 animate-spin" />
                      <span className="text-xs text-blue-400 bg-blue-900/30 px-2 py-1 rounded-lg font-medium">
                        Generating
                      </span>
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};