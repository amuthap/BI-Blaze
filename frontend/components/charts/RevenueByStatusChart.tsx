'use client';

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts';

interface RevenueByStatusData {
  name: string;
  value: number;
  count: number;
}

const COLORS = {
  paid: '#10b981',
  overdue: '#ef4444',
  unpaid: '#f59e0b',
};

export function RevenueByStatusChart() {
  const [data, setData] = useState<RevenueByStatusData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/reports/payment-status`);
        if (!response.ok) throw new Error('Failed to fetch payment status');
        const result = await response.json();

        const formatted = result.map((item: any) => ({
          name: item.status.charAt(0).toUpperCase() + item.status.slice(1),
          value: item.amount,
          count: item.count,
        }));

        setData(formatted);
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

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Status</h3>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: $${(value / 1000000).toFixed(1)}M`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[entry.name.toLowerCase() as keyof typeof COLORS] || '#8884d8'}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: any) => `$${(value / 1000000).toFixed(2)}M`}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-3 gap-4">
        {data.map((item) => (
          <div key={item.name} className="text-center">
            <p className="text-sm text-gray-600">{item.name}</p>
            <p className="text-lg font-bold text-gray-900">${(item.value / 1000000).toFixed(1)}M</p>
            <p className="text-xs text-gray-500">{item.count} invoices ({((item.value / total) * 100).toFixed(1)}%)</p>
          </div>
        ))}
      </div>
    </div>
  );
}
