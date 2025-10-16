import React from 'react';
import { VideoCategory } from '../types';
import { CATEGORY_CONFIG } from '../constants/categories';

interface Props {
  selectedCategory: VideoCategory;
  availableCategories: VideoCategory[];
  onChange: (category: VideoCategory) => void;
}

export const CategorySelector: React.FC<Props> = ({ selectedCategory, availableCategories, onChange }) => {
  const filteredCategories = availableCategories.filter(cat => cat !== 'custom');

  if (filteredCategories.length === 0) return null;

  return (
    <div className="grid gap-6 mb-8 grid-cols-1 md:grid-cols-3">
      {filteredCategories.map((cat) => {
        const config = CATEGORY_CONFIG[cat];
        const isSelected = selectedCategory === cat;

        return (
          <button
            key={cat}
            onClick={() => onChange(cat)}
            className={`p-6 rounded-2xl transition-all duration-300 text-left border-2 shadow-lg ${
              isSelected
                ? `${config.color} border-white/30 scale-105`
                : 'bg-slate-800 border-slate-700 hover:bg-slate-700 hover:border-slate-600 hover:scale-102'
            }`}
          >
            <div className="text-4xl mb-4">{config.icon}</div>
            <div className="text-xl font-bold mb-2">{config.title}</div>
            <div className="text-sm text-slate-300">{config.description}</div>
          </button>
        );
      })}
    </div>
  );
};