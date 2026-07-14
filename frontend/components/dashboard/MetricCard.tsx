'use client';

import { formatCurrency, formatNumber, formatPercentage, getChangeColor, getChangeBgColor } from '@/utils/formatters';

interface MetricCardProps {
  title: string;
  value: number;
  change: number;
  icon?: React.ReactNode;
  format?: 'currency' | 'number';
  subtitle?: string;
  onClick?: () => void;
}

export const MetricCard = ({
  title,
  value,
  change,
  icon,
  format = 'currency',
  subtitle,
  onClick,
}: MetricCardProps) => {
  const formattedValue =
    format === 'currency' ? formatCurrency(value) : formatNumber(value);

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-lg border border-gray-200 p-6 hover:border-gray-300 transition-colors ${onClick ? 'cursor-pointer hover:shadow-lg hover:border-blue-400' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="mt-2">
            <p className="text-2xl sm:text-3xl font-bold text-gray-900">
              {formattedValue}
            </p>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          <div className={`mt-4 inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${getChangeBgColor(change)} ${getChangeColor(change)}`}>
            <span className={`${change >= 0 ? '📈' : '📉'} mr-1`}></span>
            {formatPercentage(change)} from last period
          </div>
        </div>
        {icon && (
          <div className="ml-4 text-3xl opacity-80">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};
