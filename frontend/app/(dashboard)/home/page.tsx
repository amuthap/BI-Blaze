'use client';

import { useEffect, useState } from 'react';
import { useDashboard } from '@/hooks/useDashboard';
import { useDashboardStore } from '@/lib/store/dashboardStore';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { RevenueTrendChart } from '@/components/charts/RevenueTrendChart';
import { RevenueByStatusChart } from '@/components/charts/RevenueByStatusChart';
import { LoadingSkeleton, ChartSkeleton } from '@/components/common/LoadingSkeleton';
import { DetailedListModal } from '@/components/dashboard/DetailedListModal';
import { CustomerSegmentationWidget } from '@/components/dashboard/CustomerSegmentationWidget';
import { InvoiceAgingWidget } from '@/components/dashboard/InvoiceAgingWidget';
import { PaymentHealthWidget } from '@/components/dashboard/PaymentHealthWidget';
import { TopCustomersWidget } from '@/components/dashboard/TopCustomersWidget';
import { MonthlyComparisonChart } from '@/components/charts/MonthlyComparisonChart';

export default function HomePage() {
  const { metrics, revenueTrend, selectedPeriod, isLoading, error, refresh } = useDashboard();
  const { setPeriod } = useDashboardStore();
  const [mounted, setMounted] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState<'invoices' | 'payments' | 'customers' | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const handlePeriodChange = (period: 'today' | 'week' | 'month' | 'quarter' | 'year') => {
    setPeriod(period);
  };

  const openMetricDetail = (metricType: 'invoices' | 'payments' | 'customers') => {
    setSelectedMetric(metricType);
    setModalOpen(true);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Real-time business metrics and insights</p>
      </div>

      {/* Period Selector */}
      <div className="mb-8 flex gap-2 flex-wrap">
        {(['today', 'week', 'month', 'quarter', 'year'] as const).map((period) => (
          <button
            key={period}
            onClick={() => handlePeriodChange(period)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${
              selectedPeriod === period
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {period}
          </button>
        ))}
        <button
          onClick={refresh}
          disabled={isLoading}
          className="ml-auto px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
        >
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {isLoading && !metrics ? (
        <LoadingSkeleton />
      ) : (
        <>
          {/* Metrics Grid */}
          {metrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <MetricCard
                title="Total Revenue"
                value={metrics.total_revenue.value}
                change={metrics.total_revenue.change_pct}
                icon="💰"
                format="currency"
                onClick={() => openMetricDetail('payments')}
              />
              <MetricCard
                title="Invoices"
                value={metrics.invoice_count.value}
                change={metrics.invoice_count.change_pct}
                icon="📄"
                format="number"
                onClick={() => openMetricDetail('invoices')}
              />
              <MetricCard
                title="Customers"
                value={metrics.customer_count.value}
                change={metrics.customer_count.change_pct}
                icon="👥"
                format="number"
                onClick={() => openMetricDetail('customers')}
              />
              <MetricCard
                title="Avg Transaction"
                value={metrics.avg_transaction.value}
                change={metrics.avg_transaction.change_pct}
                icon="💳"
                format="currency"
                onClick={() => openMetricDetail('payments')}
              />
            </div>
          )}

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {revenueTrend ? (
              <RevenueTrendChart data={revenueTrend} />
            ) : (
              <ChartSkeleton />
            )}

            <RevenueByStatusChart />
          </div>

          {/* Advanced Analytics Section */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Advanced Analytics</h2>

            {/* First Row - Health Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              <PaymentHealthWidget />
              <InvoiceAgingWidget />
              <CustomerSegmentationWidget />
            </div>

            {/* Second Row - Trends and Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <MonthlyComparisonChart />
              <TopCustomersWidget />
            </div>
          </div>
        </>
      )}

      {/* Detailed List Modal */}
      <DetailedListModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        metricType={selectedMetric}
      />
    </div>
  );
}
