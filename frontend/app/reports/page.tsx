'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api/client';

export default function ReportsPage() {
  const [reportTitle, setReportTitle] = useState('Monthly Business Report');
  const [reportDays, setReportDays] = useState(30);
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState<{ title: string; content: string; generated_at: string } | null>(null);

  const handleGenerateReport = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.generateReport(reportTitle, reportDays);
      setReport(data);
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports</h1>
      <p className="text-gray-600 mb-8">Generate custom business reports</p>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Report Title
            </label>
            <input
              type="text"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter report title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Period (Days)
            </label>
            <select
              value={reportDays}
              onChange={(e) => setReportDays(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Last 7 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
              <option value={365}>Last Year</option>
            </select>
          </div>

          <button
            onClick={handleGenerateReport}
            disabled={isLoading}
            className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
          >
            {isLoading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
      </div>

      {report && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{report.title}</h2>
          <p className="text-sm text-gray-500 mb-4">
            Generated: {new Date(report.generated_at).toLocaleString()}
          </p>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{report.content}</p>
          </div>
        </div>
      )}
    </div>
  );
}
