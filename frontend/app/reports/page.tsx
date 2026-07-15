'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { RevenueTrendChart } from '@/components/charts/RevenueTrendChart';
import { RevenueByStatusChart } from '@/components/charts/RevenueByStatusChart';

interface DashboardData {
  metrics?: any;
  revenueTrend?: any;
  paymentHealth?: any;
}

export default function ReportsPage() {
  const [reportTitle, setReportTitle] = useState('Monthly Business Report');
  const [reportDays, setReportDays] = useState(30);
  const [reportType, setReportType] = useState('summary');
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState<{ title: string; content: string; generated_at: string } | null>(null);

  // Clear report when report type changes
  const handleReportTypeChange = (newType: string) => {
    setReportType(newType);
    setReport(null);
  };
  const [dashboardData, setDashboardData] = useState<DashboardData>({});

  // Load dashboard data for charts - reload when days or type changes
  useEffect(() => {
    const loadData = async () => {
      try {
        console.log('Loading data with:', { reportDays, reportType });
        const [metrics, trend] = await Promise.all([
          apiClient.getMetrics('month'),
          apiClient.getRevenueTrend(reportDays),
        ]);
        console.log('Data loaded:', { metrics, trend });
        setDashboardData({ metrics, revenueTrend: trend });
      } catch (err) {
        console.error('Failed to load data:', err);
      }
    };
    loadData();
  }, [reportDays, reportType]); // Reload charts when time period or report type changes

  const handleGenerateReport = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.generateReport(reportTitle, reportDays, reportType);
      setReport(data);
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Reports & Analytics</h1>
              <p className="text-gray-600 mt-1">Generate comprehensive business reports with visualizations</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Report Generator */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-4">
              <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Generate Report</h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Report Type
                    </label>
                    <select
                      value={reportType}
                      onChange={(e) => handleReportTypeChange(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 font-medium"
                    >
                      <option value="summary">Executive Summary</option>
                      <option value="detailed">Detailed Analysis</option>
                      <option value="financial">Financial Report</option>
                      <option value="sales">Sales Performance</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Report Title
                    </label>
                    <input
                      type="text"
                      value={reportTitle}
                      onChange={(e) => setReportTitle(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 font-medium placeholder-gray-400"
                      placeholder="Enter report title"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Period
                    </label>
                    <select
                      value={reportDays}
                      onChange={(e) => setReportDays(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 font-medium"
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
                    className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 font-medium transition-all flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {isLoading ? 'Generating...' : 'Generate Report'}
                  </button>
                </div>
              </div>

              {/* Info Card */}
              <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                <h3 className="font-semibold text-blue-900 mb-2 text-sm">📊 Report Includes</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✓ Executive Summary</li>
                  <li>✓ Financial Metrics</li>
                  <li>✓ Trend Analysis</li>
                  <li>✓ Key Insights</li>
                  <li>✓ Recommendations</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Right: Charts & Report */}
          <div className="lg:col-span-2 space-y-6">
            {/* Charts Section - Updated based on report type */}
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                <strong>📊 Chart Period:</strong> Last {reportDays} days | <strong>Report Type:</strong> {reportType}
              </div>

              {dashboardData.revenueTrend && (
                <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm" key={`trend-${reportDays}`}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900">
                      {reportType === 'financial' ? '💰 Revenue Trend (Financial Analysis)' : '📈 Revenue Trend'}
                    </h3>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {reportDays} days
                    </span>
                  </div>
                  <RevenueTrendChart key={`chart-${reportDays}`} data={dashboardData.revenueTrend} height={300} />
                </div>
              )}

              <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900">
                    {reportType === 'sales' ? '🎯 Payment Status (Sales View)' : '💳 Payment Status'}
                  </h3>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    Current status
                  </span>
                </div>
                <RevenueByStatusChart />
              </div>
            </div>

            {/* Generated Report */}
            {report && (
              <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{report.title}</h2>
                    <p className="text-sm text-gray-500 mt-1">
                      Generated: {new Date(report.generated_at).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      const element = document.createElement('a');
                      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(report.content));
                      element.setAttribute('download', `${report.title}.txt`);
                      element.style.display = 'none';
                      document.body.appendChild(element);
                      element.click();
                      document.body.removeChild(element);
                    }}
                    className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 font-medium transition-colors"
                  >
                    Download
                  </button>
                </div>
                <div className="prose prose-sm max-w-none">
                  <div className="text-gray-700 whitespace-pre-wrap leading-relaxed bg-gray-50 p-4 rounded-lg border border-gray-200">
                    {report.content}
                  </div>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!report && (
              <div className="bg-white rounded-lg border border-gray-200 p-12 shadow-sm text-center">
                <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-500 text-lg">Generate a report to see results here</p>
                <p className="text-gray-400 text-sm mt-2">Configure options on the left and click "Generate Report"</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
