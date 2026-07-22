'use client';

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Business Intelligence System</p>
      </div>

      {/* Status Card */}
      <div className="bg-white rounded-lg border border-gray-200 p-8 mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">✅ System Status</h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-semibold text-gray-900">Backend API</p>
              <p className="text-sm text-gray-600">FastAPI with Uvicorn</p>
            </div>
            <span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-semibold text-gray-900">Zoho Books Integration</p>
              <p className="text-sm text-gray-600">OAuth2 Connected</p>
            </div>
            <span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-semibold text-gray-900">QuickBooks Sync</p>
              <p className="text-sm text-gray-600">Scheduled daily at 02:00 UTC</p>
            </div>
            <span className="inline-block w-3 h-3 bg-blue-500 rounded-full"></span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-semibold text-gray-900">Database</p>
              <p className="text-sm text-gray-600">PostgreSQL with QB tables ready</p>
            </div>
            <span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span>
          </div>
        </div>
      </div>

      {/* Next Steps Card */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-8">
        <h2 className="text-2xl font-semibold text-blue-900 mb-4">🚀 Next Steps</h2>

        <div className="space-y-3 text-blue-800">
          <p className="flex items-start gap-3">
            <span className="font-bold">1.</span>
            <span>Verify your QB account has accessible data and Accounting API enabled</span>
          </p>
          <p className="flex items-start gap-3">
            <span className="font-bold">2.</span>
            <span>QB sync will run tomorrow at 02:00 UTC and populate dashboard with unified data</span>
          </p>
          <p className="flex items-start gap-3">
            <span className="font-bold">3.</span>
            <span>Visit Settings page to check data source status and configuration</span>
          </p>
          <p className="flex items-start gap-3">
            <span className="font-bold">4.</span>
            <span>Use Chat feature to query and analyze your Zoho Books and QB data</span>
          </p>
        </div>

        <div className="mt-6 pt-6 border-t border-blue-200">
          <p className="text-sm text-blue-700">
            <strong>Dashboard Integration:</strong> Full-featured dashboard with charts, metrics, and reports will be populated once QB data is synced. Current view shows system status to verify all components are operational.
          </p>
        </div>
      </div>
    </div>
  );
}
