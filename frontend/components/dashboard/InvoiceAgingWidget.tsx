'use client';

import { useEffect, useState } from 'react';

interface AgingBucket {
  count: number;
  amount: number;
  overdue_count: number;
}

interface InvoiceAgingData {
  aging_distribution: {
    '0-30_days': AgingBucket;
    '31-60_days': AgingBucket;
    '61-90_days': AgingBucket;
    '90_plus_days': AgingBucket;
  };
}

export function InvoiceAgingWidget() {
  const [data, setData] = useState<InvoiceAgingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/reports/invoice-aging`);
        if (!response.ok) throw new Error('Failed to fetch invoice aging');
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

  const buckets = [
    { label: '0-30 Days', key: '0-30_days', color: 'green' },
    { label: '31-60 Days', key: '31-60_days', color: 'yellow' },
    { label: '61-90 Days', key: '61-90_days', color: 'orange' },
    { label: '90+ Days', key: '90_plus_days', color: 'red' },
  ] as const;

  const maxAmount = Math.max(
    ...buckets.map((b) => data.aging_distribution[b.key].amount)
  );

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Invoice Aging</h3>

      <div className="space-y-3">
        {buckets.map((bucket) => {
          const item = data.aging_distribution[bucket.key];
          const percentage = maxAmount > 0 ? (item.amount / maxAmount) * 100 : 0;
          const colorClass = {
            green: 'bg-green-500',
            yellow: 'bg-yellow-500',
            orange: 'bg-orange-500',
            red: 'bg-red-500',
          }[bucket.color];

          return (
            <div key={bucket.key}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-gray-700">{bucket.label}</span>
                <span className="text-xs text-gray-600">
                  {item.count} invoices {item.overdue_count > 0 && `(${item.overdue_count} overdue)`}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className={`${colorClass} h-2 rounded-full`} style={{ width: `${percentage}%` }} />
              </div>
              <p className="text-xs text-gray-500 mt-1">INR {(item.amount / 100000).toFixed(2)}L</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
