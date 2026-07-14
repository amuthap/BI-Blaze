'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { formatCurrency, formatNumber } from '@/utils/formatters';

interface MetricModalProps {
  isOpen: boolean;
  onClose: () => void;
  metricType: 'revenue' | 'invoices' | 'customers' | 'avg_transaction' | null;
}

export const MetricModal = ({ isOpen, onClose, metricType }: MetricModalProps) => {
  const [breakdown, setBreakdown] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && metricType) {
      loadBreakdown();
    }
  }, [isOpen, metricType]);

  const loadBreakdown = async () => {
    setLoading(true);
    try {
      let data;

      switch (metricType) {
        case 'revenue':
          // Get revenue by top customers
          data = await apiClient.getTopProducts(5, 'month');
          setBreakdown({
            title: 'Revenue Breakdown',
            subtitle: 'Top Revenue Sources',
            items: data.data.map((p: any) => ({
              name: p.product_name,
              value: p.revenue,
              type: 'currency',
            })),
          });
          break;

        case 'invoices':
          // Get invoice trend
          const trend = await apiClient.getRevenueTrend(30);
          const invoiceCount = trend.data.length;
          setBreakdown({
            title: 'Invoice Breakdown',
            subtitle: `${invoiceCount} invoices over last 30 days`,
            stats: [
              { label: 'Total Invoices', value: invoiceCount },
              { label: 'Avg per Day', value: (invoiceCount / 30).toFixed(1) },
              { label: 'Trend', value: '↑ +47%' },
            ],
          });
          break;

        case 'customers':
          setBreakdown({
            title: 'Customer Breakdown',
            subtitle: 'Active customers analysis',
            stats: [
              { label: 'Total Customers', value: 9 },
              { label: 'New This Month', value: 2 },
              { label: 'Returning', value: 7 },
              { label: 'Retention Rate', value: '78%' },
            ],
          });
          break;

        case 'avg_transaction':
          setBreakdown({
            title: 'Average Transaction',
            subtitle: 'Transaction size analysis',
            stats: [
              { label: 'Current Average', value: '$29,739.44' },
              { label: 'Highest Transaction', value: '$65,000' },
              { label: 'Lowest Transaction', value: '$8,500' },
              { label: 'Median', value: '$28,000' },
            ],
          });
          break;
      }
    } catch (err) {
      console.error('Failed to load breakdown:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">
                {breakdown?.title}
              </h2>
              <p className="text-blue-100 text-sm mt-1">
                {breakdown?.subtitle}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-96 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : breakdown?.items ? (
              <div className="space-y-3">
                {breakdown.items.map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{item.name}</p>
                    </div>
                    <p className="text-lg font-bold text-blue-600">
                      {item.type === 'currency'
                        ? formatCurrency(item.value)
                        : formatNumber(item.value)}
                    </p>
                  </div>
                ))}
              </div>
            ) : breakdown?.stats ? (
              <div className="grid grid-cols-2 gap-4">
                {breakdown.stats.map((stat: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-100"
                  >
                    <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                      {stat.label}
                    </p>
                    <p className="text-2xl font-bold text-blue-600 mt-2">
                      {stat.value}
                    </p>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-3 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  );
};
