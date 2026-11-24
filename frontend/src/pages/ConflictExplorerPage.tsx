import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Info } from 'lucide-react';
import { getConflicts, getProduct, getProductReviews } from '../api/client';
import type { ConflictGroup, Product, Review } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ConflictCard from '../components/ConflictCard';

export default function ConflictExplorerPage() {
  const { productId } = useParams<{ productId: string }>();
  const id = Number(productId);
  const navigate = useNavigate();

  const [product, setProduct] = useState<Product | null>(null);
  const [conflicts, setConflicts] = useState<ConflictGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      getProduct(id),
      getConflicts(id),
      getProductReviews(id).catch(() => ({ data: [] as Review[] })),
    ])
      .then(([p, c]) => { setProduct(p.data); setConflicts(c.data || []); })
      .catch(() => setError('Failed to load conflicts. Run analysis first.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center"><LoadingSpinner size="lg" label="Loading conflicts…" /></div>;

  return (
    <div className="min-h-screen bg-gray-950 pt-14">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex items-center gap-3 mb-2">
          <AlertTriangle className="w-6 h-6 text-orange-400" />
          <h1 className="text-xl font-bold text-white">Conflict Explorer</h1>
        </div>
        <p className="text-gray-500 text-sm mb-8">
          {product?.name} · {conflicts.length} conflicts detected
        </p>

        {error && (
          <div className="bg-red-950/30 border border-red-800 rounded-xl p-4 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {conflicts.length === 0 && !error && (
          <div className="text-center py-16">
            <Info className="w-10 h-10 text-gray-700 mx-auto mb-3" />
            <p className="text-gray-500">No conflicts found. Run the AI analysis on this product first.</p>
          </div>
        )}

        <div className="space-y-3">
          {conflicts.map(c => (
            <ConflictCard key={c.id} conflict={c} productId={id} />
          ))}
        </div>
      </div>
    </div>
  );
}
