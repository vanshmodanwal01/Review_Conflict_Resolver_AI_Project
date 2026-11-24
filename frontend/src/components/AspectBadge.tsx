import { clsx } from 'clsx';

interface Props {
  aspect: string;
  sentiment?: 'positive' | 'negative' | 'neutral' | 'conflict';
  small?: boolean;
}

const colors: Record<string, string> = {
  positive: 'bg-emerald-900/50 text-emerald-300 border-emerald-700',
  negative: 'bg-red-900/50 text-red-300 border-red-700',
  neutral: 'bg-gray-800 text-gray-300 border-gray-600',
  conflict: 'bg-orange-900/50 text-orange-300 border-orange-700',
};

export default function AspectBadge({ aspect, sentiment = 'neutral', small }: Props) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border font-medium capitalize',
        small ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs',
        colors[sentiment]
      )}
    >
      {aspect}
    </span>
  );
}
