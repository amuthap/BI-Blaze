'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

interface PaymentHealthData {
  collection_rate: number;
  status_breakdown: {
    paid: number;
    unpaid: number;
    overdue: number;
    total: number;
  };
  days_sales_outstanding: number;
  at_risk_amount: number;
}

export function PaymentHealthWidget() {
  const [data, setData] = useState<PaymentHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/reports/payment-health`);
        if (!response.ok) throw new Error('Failed to fetch payment health');
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Health</h3>

      <div className="space-y-4">
        {/* Collection Rate */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Collection Rate</span>
            <span className="text-2xl font-bold text-green-600">{data.collection_rate}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full"
              style={{ width: `${Math.min(data.collection_rate, 100)}%` }}
            />
          </div>
        </div>

        {/* DSO */}
        <div className="bg-blue-50 rounded p-3">
          <p className="text-sm text-gray-600">Days Sales Outstanding</p>
          <p className="text-3xl font-bold text-blue-600">{data.days_sales_outstanding} days</p>
        </div>

        {/* Status Breakdown */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-green-50 rounded p-3 text-center">
            <p className="text-xs text-gray-600">Paid</p>
            <p className="text-xl font-bold text-green-600">{data.status_breakdown.paid}</p>
          </div>
          <div className="bg-yellow-50 rounded p-3 text-center">
            <p className="text-xs text-gray-600">Unpaid</p>
            <p className="text-xl font-bold text-yellow-600">{data.status_breakdown.unpaid}</p>
          </div>
          <div className="bg-red-50 rounded p-3 text-center">
            <p className="text-xs text-gray-600">Overdue</p>
            <p className="text-xl font-bold text-red-600">{data.status_breakdown.overdue}</p>
          </div>
        </div>

        {/* At Risk Amount */}
        <div className="bg-red-50 rounded p-3 border border-red-200">
          <p className="text-sm text-gray-600">At Risk Amount</p>
          <p className="text-2xl font-bold text-red-600">INR {(data.at_risk_amount / 100000).toFixed(2)}L</p>
        </div>
      </div>
    </div>
  );
}
