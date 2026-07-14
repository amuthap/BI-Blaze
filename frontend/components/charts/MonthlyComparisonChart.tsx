'use client';

import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

interface MonthlyData {
  month: string;
  revenue: number;
  invoices: number;
  unique_customers: number;
  avg_invoice: number;
  growth_pct: number;
}

interface MonthlyComparisonData {
  monthly_trends: MonthlyData[];
}

export function MonthlyComparisonChart() {
  const [data, setData] = useState<MonthlyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'revenue' | 'growth'>('revenue');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/reports/monthly-comparison`);
        if (!response.ok) throw new Error('Failed to fetch monthly comparison');
        const result = await response.json();
        setData(result.data.monthly_trends || []);
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
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Monthly Trends</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setChartType('revenue')}
            className={`px-3 py-1 text-sm rounded ${
              chartType === 'revenue' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Revenue
          </button>
          <button
            onClick={() => setChartType('growth')}
            className={`px-3 py-1 text-sm rounded ${
              chartType === 'growth' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Growth
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        {chartType === 'revenue' ? (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: any) => [`INR ${(value / 1000000).toFixed(2)}M`, '']}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px' }}
            />
            <Legend />
            <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" />
            <Bar dataKey="avg_invoice" fill="#10b981" name="Avg Invoice" />
          </BarChart>
        ) : (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} label={{ value: 'Growth %', angle: -90, position: 'insideLeft' }} />
            <Tooltip formatter={(value: any) => `${value.toFixed(2)}%`} />
            <Legend />
            <Line
              type="monotone"
              dataKey="growth_pct"
              stroke="#8b5cf6"
              name="Monthly Growth %"
              dot={{ fill: '#8b5cf6', r: 4 }}
            />
          </LineChart>
        )}
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t">
        <div>
          <p className="text-xs text-gray-600">Total Months</p>
          <p className="text-xl font-bold text-gray-900">{data.length}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600">Avg Monthly Revenue</p>
          <p className="text-lg font-bold text-blue-600">
INR {(data.reduce((sum, m) => sum + m.revenue, 0) / data.length / 1000000).toFixed(2)}M
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-600">Latest Growth</p>
          <p
            className={`text-lg font-bold ${
              data[data.length - 1]?.growth_pct >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {data[data.length - 1]?.growth_pct.toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  );
}
