import { clsx } from 'clsx';
import { Link } from 'react-router-dom';
import { AlertTriangle, ChevronRight } from 'lucide-react';
import type { ConflictGroup } from '../types';
import AspectBadge from './AspectBadge';

interface Props {
  conflict: ConflictGroup;
  productId: number;
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    score > 0.7 ? 'bg-red-500' : score > 0.4 ? 'bg-orange-400' : 'bg-yellow-400';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div className={clsx('h-full rounded-full', color)} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-400 w-9 text-right">{pct}%</span>
    </div>
  );
}

export default function ConflictCard({ conflict, productId }: Props) {
  return (
    <Link
      to={`/products/${productId}/conflicts/${conflict.id}`}
      className="block bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-brand-600 transition-colors group"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <AspectBadge aspect={conflict.aspect} sentiment="conflict" />
              <span className="text-xs text-gray-500 capitalize">{conflict.conflict_type.replace(/_/g, ' ')}</span>
            </div>
            {conflict.description && (
              <p className="text-sm text-gray-400 mt-1 line-clamp-2">{conflict.description}</p>
            )}
          </div>
        </div>
        <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-brand-400 flex-shrink-0 mt-1 transition-colors" />
      </div>

      <div className="mt-3 space-y-1">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Conflict intensity</span>
          <span className="text-orange-400">{conflict.positive_count}+ vs {conflict.negative_count}−</span>
        </div>
        <ScoreBar score={conflict.conflict_score} />
      </div>
    </Link>
  );
}
