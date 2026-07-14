'use client';

export const LoadingSkeleton = () => (
  <div className="animate-pulse">
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-gray-200 rounded-lg p-6 h-32" />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="bg-gray-200 rounded-lg p-6 h-80" />
        ))}
      </div>
    </div>
  </div>
);

export const ChartSkeleton = () => (
  <div className="animate-pulse bg-white rounded-lg border border-gray-200 p-6 h-80">
    <div className="h-4 bg-gray-200 rounded w-1/4 mb-4" />
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="h-16 bg-gray-200 rounded"
          style={{ width: `${Math.random() * 40 + 60}%` }}
        />
      ))}
    </div>
  </div>
);
