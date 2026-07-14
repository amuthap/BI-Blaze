'use client';

import { useEffect, useState } from 'react';

interface Product {
  name: string;
  sku: string;
  quantity_sold: number;
  revenue: number;
  avg_price: number;
}

interface ProductAnalysisData {
  top_performers: Product[];
  bottom_performers: Product[];
  total_products: number;
  avg_revenue_per_product: number;
}

export function ProductAnalysisWidget() {
  const [data, setData] = useState<ProductAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTop, setShowTop] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/reports/product-analysis`);
        if (!response.ok) throw new Error('Failed to fetch product analysis');
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
    return <div className="bg-white rounded-lg shadow p-6 animate-pulse h-80"></div>;
  }

  if (error || !data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600">{error || 'No data available'}</p>
      </div>
    );
  }

  const products = showTop ? data.top_performers : data.bottom_performers;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Product Performance</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setShowTop(true)}
            className={`px-3 py-1 text-sm rounded ${
              showTop ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Top
          </button>
          <button
            onClick={() => setShowTop(false)}
            className={`px-3 py-1 text-sm rounded ${
              !showTop ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
            }`}
          >
            Bottom
          </button>
        </div>
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto">
        {products.map((product, idx) => (
          <div key={idx} className="flex justify-between items-start pb-2 border-b last:border-b-0">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{product.name}</p>
              <p className="text-xs text-gray-500">{product.sku}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-900">
                INR {(product.revenue / 100000).toFixed(2)}L
              </p>
              <p className="text-xs text-gray-500">{product.quantity_sold} sold</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-600">Total Products</p>
          <p className="text-lg font-bold text-gray-900">{data.total_products}</p>
        </div>
        <div>
          <p className="text-xs text-gray-600">Avg Revenue/Product</p>
          <p className="text-lg font-bold text-blue-600">
            INR {(data.avg_revenue_per_product / 100000).toFixed(2)}L
          </p>
        </div>
      </div>
    </div>
  );
}
