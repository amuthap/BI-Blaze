'use client';

import { useEffect, useState } from 'react';

interface TopCustomer {
  customer_id: number;
  name: string;
  invoice_count: number;
  total_spent: number;
}

export function TopCustomersWidget() {
  const [data, setData] = useState<TopCustomer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/reports/top-customers?limit=5`);
        if (!response.ok) throw new Error('Failed to fetch top customers');
        const result = await response.json();

        setData(result);

        const totalRevenue = result.reduce((sum: number, c: TopCustomer) => sum + c.total_spent, 0);
        setTotal(totalRevenue);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-6 h-80 animate-pulse"></div>;
  }

  if (error || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600">{error || 'No data available'}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 5 Customers</h3>

      <div className="space-y-4">
        {data.map((customer, idx) => {
          const percentage = ((customer.total_spent / total) * 100).toFixed(1);
          return (
            <div key={customer.customer_id} className="border-b pb-3 last:border-b-0">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{idx + 1}. {customer.name}</p>
                  <p className="text-sm text-gray-500">{customer.invoice_count} invoices</p>
                </div>
                <span className="text-lg font-bold text-blue-600">${(customer.total_spent / 1000000).toFixed(1)}M</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">{percentage}% of top 5 revenue</p>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t">
        <div className="flex justify-between">
          <span className="text-gray-600">Combined Top 5 Revenue:</span>
          <span className="font-bold text-gray-900">${(total / 1000000).toFixed(1)}M</span>
        </div>
      </div>
    </div>
  );
}
