import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, TrendingUp, Laptop, ChevronRight } from 'lucide-react';
import { searchProducts, listProducts } from '../api/client';
import type { Product } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Product[]>([]);
  const [recent, setRecent] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [recentLoading, setRecentLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    listProducts(0, 6)
      .then(r => setRecent(r.data || []))
      .catch(() => {})
      .finally(() => setRecentLoading(false));
  }, []);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const r = await searchProducts(query.trim());
      setResults(r.data || []);
      if ((r.data || []).length === 0) setError('No products found. Try a different search term.');
    } catch {
      setError('Search failed. Make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  }, [query]);

  const displayList = query ? results : recent;

  return (
    <div className="min-h-screen bg-gray-950 pt-14">
      {/* Hero */}
      <div className="max-w-3xl mx-auto px-4 pt-16 pb-10 text-center">
        <div className="inline-flex items-center gap-2 bg-brand-900/40 border border-brand-700/50 rounded-full px-4 py-1.5 text-sm text-brand-300 mb-6">
          <TrendingUp className="w-4 h-4" />
          AI-Powered Review Intelligence
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight">
          Why Do Customers Disagree?
        </h1>
        <p className="text-lg text-gray-400 mb-10">
          Search for any laptop to discover conflicting opinions and understand{' '}
          <span className="text-brand-300 font-medium">why</span> different customers have
          completely different experiences.
        </p>

        {/* Search bar */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder='Try "Dell XPS" or "MacBook Air"…'
              className="w-full pl-11 pr-4 py-3.5 bg-gray-900 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-medium rounded-xl transition-colors flex items-center gap-2"
          >
            {loading ? <LoadingSpinner size="sm" /> : <Search className="w-4 h-4" />}
            {loading ? 'Searching…' : 'Search'}
          </button>
        </form>

        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}
      </div>

      {/* Results */}
      <div className="max-w-3xl mx-auto px-4 pb-16">
        {!query && (
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Available Products
          </h2>
        )}
        {recentLoading && !query && <LoadingSpinner className="mt-8" label="Loading products…" />}

        <div className="grid gap-3">
          {displayList.map(p => (
            <button
              key={p.id}
              onClick={() => navigate(`/products/${p.id}`)}
              className="flex items-center gap-4 bg-gray-900 border border-gray-800 hover:border-brand-600 rounded-xl p-4 text-left transition-colors group w-full"
            >
              <div className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center flex-shrink-0">
                <Laptop className="w-5 h-5 text-brand-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-white truncate">{p.name}</p>
                <p className="text-sm text-gray-500">
                  {p.brand} · {p.category}
                  {p.model_number ? ` · ${p.model_number}` : ''}
                </p>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-brand-400 flex-shrink-0 transition-colors" />
            </button>
          ))}
        </div>

        {displayList.length === 0 && !loading && !recentLoading && (
          <div className="text-center py-12 text-gray-600">
            <Laptop className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No products yet. Add data via the backend seed script.</p>
          </div>
        )}
      </div>
    </div>
  );
}
