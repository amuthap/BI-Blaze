'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await apiClient.healthCheck();
        setHealth(data);
      } catch (err) {
        console.error('Health check failed:', err);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
      <p className="text-gray-600 mb-8">System configuration and status</p>

      {/* System Status */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>

        {loading ? (
          <p className="text-gray-600">Checking system status...</p>
        ) : health ? (
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Status</span>
              <span className="font-medium">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                {health.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Application</span>
              <span className="font-medium">{health.app}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Environment</span>
              <span className="font-medium capitalize">{health.env}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Version</span>
              <span className="font-medium">{health.version}</span>
            </div>
          </div>
        ) : (
          <p className="text-red-600">Failed to fetch system status</p>
        )}
      </div>

      {/* API Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">API Configuration</h2>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-600">API Base URL</span>
            <span className="font-mono text-sm">{process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Environment</span>
            <span className="font-medium">Development</span>
          </div>
        </div>
      </div>
    </div>
  );
}
