import { Link, useLocation } from 'react-router-dom';
import { Brain, Search, BarChart2, Zap } from 'lucide-react';
import { clsx } from 'clsx';

const links = [
  { to: '/', label: 'Search', icon: Search },
  { to: '/analysis', label: 'Analysis', icon: BarChart2 },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-gray-900/80 backdrop-blur border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center h-14 gap-6">
        <Link to="/" className="flex items-center gap-2 font-bold text-white">
          <Brain className="w-5 h-5 text-brand-400" />
          <span className="hidden sm:block text-sm">Review Conflict Resolver</span>
          <span className="sm:hidden text-sm">RCR</span>
        </Link>

        <div className="flex items-center gap-1 ml-auto">
          {links.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors',
                pathname === to
                  ? 'bg-brand-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <Zap className="w-4 h-4" />
            API
          </a>
        </div>
      </div>
    </nav>
  );
}
