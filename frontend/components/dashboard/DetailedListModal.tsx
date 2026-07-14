'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { formatCurrency, formatDate } from '@/utils/formatters';

interface DetailedListModalProps {
  isOpen: boolean;
  onClose: () => void;
  metricType: 'invoices' | 'payments' | 'customers' | null;
}

export const DetailedListModal = ({ isOpen, onClose, metricType }: DetailedListModalProps) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [offset, setOffset] = useState(0);
  const limit = 10;

  useEffect(() => {
    if (isOpen && metricType) {
      loadData();
    }
  }, [isOpen, metricType, offset]);

  const loadData = async () => {
    setLoading(true);
    try {
      let result;

      switch (metricType) {
        case 'invoices':
          result = await apiClient.getInvoicesList(limit, offset);
          break;
        case 'payments':
          result = await apiClient.getPaymentsList(limit, offset);
          break;
        case 'customers':
          result = await apiClient.getCustomersList(limit, offset);
          break;
        default:
          result = null;
      }

      setData(result);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getTitles = () => {
    switch (metricType) {
      case 'invoices':
        return 'Invoices List';
      case 'payments':
        return 'Payments List';
      case 'customers':
        return 'Customers List';
      default:
        return 'Details';
    }
  };

  const getColumns = () => {
    switch (metricType) {
      case 'invoices':
        return [
          { key: 'invoice_number', label: 'Invoice #' },
          { key: 'date', label: 'Date' },
          { key: 'customer_name', label: 'Customer' },
          { key: 'email', label: 'Email' },
          { key: 'amount', label: 'Amount', format: 'currency' },
          { key: 'status', label: 'Status' },
        ];
      case 'payments':
        return [
          { key: 'reference_number', label: 'Reference #' },
          { key: 'date', label: 'Date' },
          { key: 'customer_name', label: 'Customer' },
          { key: 'invoice_number', label: 'Invoice' },
          { key: 'amount', label: 'Amount', format: 'currency' },
          { key: 'method', label: 'Method' },
        ];
      case 'customers':
        return [
          { key: 'name', label: 'Name' },
          { key: 'email', label: 'Email' },
          { key: 'phone', label: 'Phone' },
          { key: 'city', label: 'City' },
          { key: 'invoices', label: 'Invoices' },
          { key: 'total_spent', label: 'Total Spent', format: 'currency' },
        ];
      default:
        return [];
    }
  };

  const columns = getColumns();
  const hasNextPage = data && (offset + limit) < data.total;
  const hasPrevPage = offset > 0;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />

      {/* Modal */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-5xl max-h-[90vh] flex flex-col">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden flex flex-col h-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">{getTitles()}</h2>
              <p className="text-blue-100 text-sm mt-1">
                Showing {offset + 1} - {Math.min(offset + limit, data?.total || 0)} of {data?.total || 0} records
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
          <div className="flex-1 overflow-auto px-6 py-4">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : data && data.data && data.data.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      {columns.map((col) => (
                        <th
                          key={col.key}
                          className="text-left py-3 px-4 font-semibold text-gray-700 text-sm"
                        >
                          {col.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.data.map((row: any, idx: number) => (
                      <tr
                        key={idx}
                        className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                      >
                        {columns.map((col) => (
                          <td key={col.key} className="py-3 px-4 text-sm text-gray-800">
                            {col.format === 'currency'
                              ? formatCurrency(row[col.key])
                              : col.key === 'date'
                              ? formatDate(row[col.key])
                              : row[col.key]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                No records found
              </div>
            )}
          </div>

          {/* Footer with Pagination */}
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
            <div className="flex gap-2">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={!hasPrevPage}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                ← Previous
              </button>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={!hasNextPage}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                Next →
              </button>
            </div>
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
