import { clsx } from 'clsx';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

interface Props {
  text: string;
  position: 'supporting' | 'opposing';
  source?: string;
  rating?: number;
}

export default function EvidenceBox({ text, position, source, rating }: Props) {
  const isSupporting = position === 'supporting';
  return (
    <div
      className={clsx(
        'rounded-lg border p-3 text-sm',
        isSupporting
          ? 'border-emerald-800 bg-emerald-950/40'
          : 'border-red-800 bg-red-950/40'
      )}
    >
      <div className="flex items-center gap-2 mb-1.5">
        {isSupporting ? (
          <ThumbsUp className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
        ) : (
          <ThumbsDown className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
        )}
        <span className={clsx('text-xs font-medium', isSupporting ? 'text-emerald-400' : 'text-red-400')}>
          {isSupporting ? 'Supporting' : 'Opposing'}
        </span>
        {source && <span className="ml-auto text-xs text-gray-500 capitalize">{source}</span>}
        {rating && <span className="text-xs text-yellow-400">★ {rating}</span>}
      </div>
      <p className="text-gray-200 leading-relaxed italic">"{text}"</p>
    </div>
  );
}
