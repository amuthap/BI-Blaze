'use client';

import { ChatMessage as ChatMessageType } from '@/lib/types';
import ReactMarkdown from 'react-markdown';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 px-2`}>
      <div
        className={`max-w-2xl px-4 py-3 rounded-lg shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-none'
            : 'bg-white border border-gray-200 text-gray-900 rounded-bl-none'
        }`}
      >
        {isUser ? (
          <div>
            <p className="text-sm font-medium mb-1">You</p>
            <p className="text-sm leading-relaxed">{message.content}</p>
          </div>
        ) : (
          <div>
            <p className="text-sm font-semibold text-blue-600 mb-2">AI Assistant</p>
            <div className="text-sm prose prose-sm max-w-none leading-relaxed">
              <ReactMarkdown
                components={{
                  p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
                  ul: ({ node, ...props }) => (
                    <ul className="list-none space-y-2 mb-3" {...props} />
                  ),
                  li: ({ node, ...props }) => (
                    <li className="flex gap-2">
                      <span className="text-blue-600 font-bold">•</span>
                      <span {...props} />
                    </li>
                  ),
                  ol: ({ node, ...props }) => (
                    <ol className="list-none space-y-2 mb-3 counter-reset" {...props} />
                  ),
                  code: ({ node, inline, ...props }: any) =>
                    inline ? (
                      <code className="bg-blue-50 text-blue-900 px-2 py-0.5 rounded text-xs font-mono border border-blue-100" {...props} />
                    ) : (
                      <pre className="bg-gray-100 text-gray-800 p-3 rounded-lg mb-3 overflow-auto text-xs" {...props} />
                    ),
                  strong: ({ node, ...props }) => <strong className="font-bold text-gray-900" {...props} />,
                  em: ({ node, ...props }) => <em className="italic text-gray-700" {...props} />,
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}
        <p className={`text-xs mt-2 opacity-60 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
};
