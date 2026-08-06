'use client';

import { useEffect, useState } from 'react';

interface Customer {
  name: string;
  invoices: number;
  total_value: number;
  avg_invoice: number;
}

interface SegmentationData {
  summary: {
    high_count: number;
    medium_count: number;
    low_count: number;
    high_revenue: number;
    medium_revenue: number;
    low_revenue: number;
  };
}

export function CustomerSegmentationWidget() {
  const [data, setData] = useState<SegmentationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/reports/customer-segmentation`);
        if (!response.ok) throw new Error('Failed to fetch customer segmentation');
        const result = await response.json();
        setData(result.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-6 animate-pulse h-64"></div>;
  }

  if (error || !data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600">{error || 'No data available'}</p>
      </div>
    );
  }

  const segments = [
    {
      label: 'High Value',
      icon: '👑',
      count: data.summary.high_count,
      revenue: data.summary.high_revenue,
      color: 'purple',
    },
    {
      label: 'Medium Value',
      icon: '📈',
      count: data.summary.medium_count,
      revenue: data.summary.medium_revenue,
      color: 'blue',
    },
    {
      label: 'Low Value',
      icon: '📊',
      count: data.summary.low_count,
      revenue: data.summary.low_revenue,
      color: 'gray',
    },
  ];

  const colorClasses = {
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    gray: 'bg-gray-50 border-gray-200 text-gray-700',
  };

  const totalRevenue =
    data.summary.high_revenue + data.summary.medium_revenue + data.summary.low_revenue;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Segmentation</h3>

      <div className="space-y-3">
        {segments.map((segment) => {
          const percentage = totalRevenue > 0 ? (segment.revenue / totalRevenue) * 100 : 0;
          const colorClass = colorClasses[segment.color as keyof typeof colorClasses];

          return (
            <div key={segment.label} className={`border rounded p-3 ${colorClass}`}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">
                  {segment.icon} {segment.label}
                </span>
                <span className="text-xs font-semibold">{segment.count} customers</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold">INR {(segment.revenue / 1000000).toFixed(1)}M</span>
                <span className="text-xs">{percentage.toFixed(1)}%</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-4 border-t">
        <p className="text-xs text-gray-600">Total Customer Base</p>
        <p className="text-xl font-bold text-gray-900">
          {data.summary.high_count + data.summary.medium_count + data.summary.low_count}
        </p>
      </div>
    </div>
  );
}
