'use client';

import { useEffect, useState } from 'react';
import { useChat } from '@/hooks/useDashboard';
import { ChatWindow } from '@/components/chat/ChatWindow';

export default function ChatPage() {
  const { messages, currentConversationId, sendMessage, setCurrentConversation } = useChat();
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSendMessage = async (message: string) => {
    setIsLoading(true);
    try {
      await sendMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-80px)]">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Ask Questions</h1>
        <p className="text-gray-600 mt-2">
          Chat with AI to analyze your business data. Ask about revenue trends, top products, customer metrics, and more.
        </p>
      </div>

      {/* Conversation Selector */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setCurrentConversation('default')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            currentConversationId === 'default'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Main Chat
        </button>
      </div>

      {/* Chat Window */}
      <div className="flex-1">
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
