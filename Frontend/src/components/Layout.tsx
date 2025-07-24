import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const navLinks = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/boards', label: 'Boards' },
];

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r hidden md:flex flex-col">
        <div className="h-16 flex items-center justify-center border-b">
          <span className="text-xl font-bold text-blue-700">FeedbackPro</span>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`block px-4 py-2 rounded-lg font-medium transition-colors ${location.pathname.startsWith(link.to) ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t mt-auto">
          <div className="text-sm text-gray-600 mb-2">{user?.first_name} {user?.last_name}</div>
          <button className="btn btn-danger w-full" onClick={logout}>Sign Out</button>
        </div>
      </aside>
      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Topbar */}
        <header className="h-16 bg-white border-b flex items-center px-4 md:hidden justify-between">
          <span className="text-lg font-bold text-blue-700">FeedbackPro</span>
          <button className="btn btn-danger btn-xs" onClick={logout}>Sign Out</button>
        </header>
        <main className="flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}; 