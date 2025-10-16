import React from 'react';
import { X } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

export const Notification: React.FC = () => {
  const { notification, showNotification } = useApp();

  if (!notification) return null;

  const bgColor = {
    success: 'bg-emerald-600',
    error: 'bg-red-600',
    info: 'bg-blue-600'
  }[notification.type];

  return (
    <div className={`fixed top-6 right-6 z-50 p-4 rounded-xl shadow-2xl ${bgColor} max-w-sm animate-in slide-in-from-right`}>
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-white pr-2">{notification.message}</p>
        <button
          onClick={() => showNotification('', 'success')}
          className="text-white hover:text-gray-200 flex-shrink-0 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};