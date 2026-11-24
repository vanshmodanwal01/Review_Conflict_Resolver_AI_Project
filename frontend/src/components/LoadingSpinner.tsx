import { clsx } from 'clsx';

interface Props {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export default function LoadingSpinner({ size = 'md', className, label }: Props) {
  const sizeClass = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className={clsx('flex flex-col items-center gap-3', className)}>
      <div className={clsx('border-4 border-gray-700 border-t-brand-400 rounded-full animate-spin', sizeClass)} />
      {label && <p className="text-sm text-gray-400">{label}</p>}
    </div>
  );
}
