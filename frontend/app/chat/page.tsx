'use client';

import { useEffect, useState } from 'react';
import { useChat } from '@/hooks/useDashboard';
import { ChatWindow } from '@/components/chat/ChatWindow';

const SUGGESTED_QUESTIONS = [
  "What's our total revenue this year?",
  "Which are our top selling products?",
  "Show me the customer segmentation analysis",
  "How many invoices are overdue?",
  "What's the payment health status?",
  "Which customers have the highest lifetime value?",
];

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

  const handleSuggestedQuestion = async (question: string) => {
    await handleSendMessage(question);
  };

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Business Intelligence Assistant</h1>
              <p className="text-gray-600 mt-1">Ask questions about your Zoho Books data and get instant insights</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Chat Area */}
          <div className="lg:col-span-3">
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>

          {/* Suggested Questions Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-4">
              <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-3 text-sm">💡 Quick Questions</h3>
                <div className="space-y-2">
                  {SUGGESTED_QUESTIONS.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestedQuestion(question)}
                      disabled={isLoading}
                      className="w-full text-left text-sm px-3 py-2 text-gray-700 bg-gray-50 hover:bg-blue-50 rounded border border-gray-100 hover:border-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>

              {/* Info Card */}
              <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                <h3 className="font-semibold text-gray-900 mb-3 text-sm">📊 Data Coverage</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center justify-between">
                    <span>Invoices</span>
                    <span className="font-semibold text-gray-900">1,624</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Customers</span>
                    <span className="font-semibold text-gray-900">81</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Products</span>
                    <span className="font-semibold text-gray-900">94</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Total Revenue</span>
                    <span className="font-semibold text-gray-900">$911K</span>
                  </div>
                </div>
              </div>

              {/* Tips Card */}
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                <h3 className="font-semibold text-blue-900 mb-2 text-sm">💬 Tips</h3>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• Be specific with questions</li>
                  <li>• Ask about trends</li>
                  <li>• Request comparisons</li>
                  <li>• Ask for analysis</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
