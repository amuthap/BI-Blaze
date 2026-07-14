'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const Header = () => {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path || pathname?.startsWith(path + '/');
  };

  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/home" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">📊</span>
            </div>
            <span className="hidden sm:inline font-semibold text-gray-900">BI Dashboard</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex gap-1">
            <NavLink href="/home" label="Dashboard" active={isActive('/home')} />
            <NavLink href="/chat" label="Chat" active={isActive('/chat')} />
            <NavLink href="/reports" label="Reports" active={isActive('/reports')} />
            <NavLink href="/settings" label="Settings" active={isActive('/settings')} />
          </nav>

          {/* User Menu Placeholder */}
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
              Profile
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

const NavLink = ({ href, label, active }: { href: string; label: string; active: boolean }) => (
  <Link
    href={href}
    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
      active
        ? 'bg-blue-50 text-blue-700'
        : 'text-gray-700 hover:bg-gray-50'
    }`}
  >
    {label}
  </Link>
);
