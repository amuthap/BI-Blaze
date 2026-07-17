'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null);
  const [qbStatus, setQbStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [qbLoading, setQbLoading] = useState(false);

  const fetchQBStatus = async () => {
    try {
      const qbData = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/quickbooks/status`)
        .then(r => r.json())
        .catch(() => ({ connected: false }));
      setQbStatus(qbData);
      return qbData;
    } catch (err) {
      console.error('Failed to fetch QB status:', err);
      return { connected: false };
    }
  };

  useEffect(() => {
    const checkHealth = async () => {
      try {
        console.log('=== Settings Page Loading ===');
        console.log('URL:', window.location.href);
        console.log('Search params:', window.location.search);

        const data = await apiClient.healthCheck();
        setHealth(data);
        console.log('Health check passed');

        // Check for OAuth callback query parameters FIRST
        const params = new URLSearchParams(window.location.search);
        const qbParam = params.get('qb');
        console.log('QB Param:', qbParam);

        if (qbParam === 'success') {
          console.log('✅ QuickBooks authorization successful!');
          // Clean up URL immediately
          window.history.replaceState({}, document.title, window.location.pathname);
          // Fetch latest status
          console.log('Fetching updated QB status...');
          const updatedStatus = await fetchQBStatus();
          console.log('Updated status:', updatedStatus);
          // Show success message
          alert('QuickBooks authorized successfully! Connection status: ' +
            (updatedStatus?.connected ? 'Connected' : 'Pending'));
        } else if (qbParam === 'error') {
          console.log('❌ QuickBooks authorization failed');
          // Clean up URL
          window.history.replaceState({}, document.title, window.location.pathname);
          alert('Failed to authorize QuickBooks. Please check the server logs for details.');
          // Still fetch status
          await fetchQBStatus();
        } else {
          console.log('Normal page load - fetching QB status...');
          // Normal page load - just fetch status
          await fetchQBStatus();
        }
      } catch (err) {
        console.error('❌ Error during setup:', err);
        // Still try to load QB status
        await fetchQBStatus();
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  const handleAuthorizeQB = async () => {
    setQbLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/quickbooks/authorize`)
        .then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        });

      if (!response.authorization_url) {
        throw new Error('No authorization URL received from server');
      }

      console.log('Redirecting to QuickBooks authorization...');
      window.location.href = response.authorization_url;
    } catch (err) {
      console.error('Failed to get authorization URL:', err);
      alert(`Failed to authorize QuickBooks: ${err instanceof Error ? err.message : String(err)}`);
      setQbLoading(false);
    }
  };

  const handleDisconnectQB = async () => {
    if (!confirm('Are you sure you want to disconnect QuickBooks?')) return;

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/quickbooks/disconnect`, {
        method: 'POST'
      });
      setQbStatus({ connected: false });
      alert('QuickBooks disconnected successfully');
    } catch (err) {
      console.error('Failed to disconnect QuickBooks:', err);
      alert('Failed to disconnect QuickBooks. Please try again.');
    }
  };

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
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
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

      {/* Data Sources */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Connected Data Sources</h2>
        <div className="space-y-4">
          {/* Zoho Books */}
          <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                Zoho Books
              </h3>
              <p className="text-sm text-gray-600 mt-1">Primary accounting system - Active</p>
            </div>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Connected</span>
          </div>

          {/* QuickBooks */}
          <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <span className={`inline-block w-2 h-2 rounded-full ${qbStatus?.connected ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                QuickBooks Online (Virtunest)
              </h3>
              <p className={`text-sm mt-1 ${qbStatus?.last_sync_status === 'failed' ? 'text-red-600 font-semibold' : 'text-gray-600'}`}>
                {qbStatus?.message || (qbStatus?.connected ? 'Connected' : 'Not yet connected - Click to authorize')}
              </p>
            </div>
            <div>
              {qbStatus?.connected ? (
                <button
                  onClick={handleDisconnectQB}
                  className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 transition-colors"
                >
                  Disconnect
                </button>
              ) : (
                <button
                  onClick={handleAuthorizeQB}
                  disabled={qbLoading}
                  className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {qbLoading ? 'Authorizing...' : 'Connect'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h3 className="font-semibold text-blue-900 mb-2">🔄 Unified Reporting</h3>
        <p className="text-sm text-blue-800 mb-3">
          Your BI system automatically combines data from both Zoho Books and QuickBooks to provide comprehensive insights.
        </p>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Reports aggregate data from both sources</li>
          <li>✓ Overdue invoices, payments, and revenue tracked from both systems</li>
          <li>✓ Unified customer and product analysis</li>
          <li>✓ Automatic daily syncing from both platforms</li>
        </ul>
      </div>
    </div>
  );
}
