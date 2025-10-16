import React from 'react';
import { X, Youtube, Download, Loader } from 'lucide-react';
import { VideoMetadata } from '../types';
import { useDownload } from '../hooks/useDownload';

interface Props {
  videoName: string;
  metadata: VideoMetadata;
  onClose: () => void;
}

export const MetadataModal: React.FC<Props> = ({ videoName, metadata, onClose }) => {
  const { downloading, downloadMetadata } = useDownload();

  return (
    <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-slate-700/50 shadow-2xl">
        <div className="sticky top-0 bg-gradient-to-r from-slate-800 to-slate-900 border-b border-slate-700 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold flex items-center">
              <Youtube className="w-8 h-8 mr-3 text-red-500" />
              YouTube Metadata
            </h2>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-blue-400">Title</h3>
            <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600">
              <p className="text-white">{metadata.title}</p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2 text-blue-400">Description</h3>
            <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600">
              <p className="text-white whitespace-pre-wrap">{metadata.description}</p>
            </div>
          </div>

          {metadata.timestamps && metadata.timestamps.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2 text-blue-400">Timestamps / Chapters</h3>
              <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600">
                {metadata.timestamps.map((ts, idx) => (
                  <p key={idx} className="text-white mb-1">{ts}</p>
                ))}
              </div>
            </div>
          )}

          {metadata.tags && metadata.tags.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2 text-blue-400">Tags</h3>
              <div className="bg-slate-700/50 rounded-xl p-4 border border-slate-600">
                <div className="flex flex-wrap gap-2">
                  {metadata.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-900/50 text-blue-300 px-3 py-1 rounded-full text-sm border border-blue-700/30 font-medium"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          <button
            onClick={() => downloadMetadata(videoName)}
            disabled={downloading[`metadata-${videoName}`]}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-3 px-6 rounded-xl font-bold transition-all flex items-center justify-center shadow-lg"
          >
            {downloading[`metadata-${videoName}`] ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Download className="w-5 h-5 mr-2" />
                Download as Text File
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};