import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import { ArrowLeft, TrendingUp } from 'lucide-react';
import { getAnalysisSummary, getProduct } from '../api/client';
import type { AnalysisSummary, Product } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import AspectBadge from '../components/AspectBadge';

const SENTIMENT_COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#6b7280' };
const RATING_COLORS = ['#ef4444', '#f97316', '#f59e0b', '#84cc16', '#10b981'];

export default function AnalysisDashboardPage() {
  const { productId } = useParams<{ productId: string }>();
  const id = Number(productId);
  const navigate = useNavigate();

  const [product, setProduct] = useState<Product | null>(null);
  const [summary, setSummary] = useState<AnalysisSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([getProduct(id), getAnalysisSummary(id)])
      .then(([p, s]) => { setProduct(p.data); setSummary(s.data); })
      .catch(() => setError('Failed to load analysis. Have you run the analysis yet?'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center"><LoadingSpinner size="lg" label="Loading analysis…" /></div>;
  if (error || !summary) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center text-red-400 text-center px-4">{error}</div>;

  const ratingData = Object.entries(summary.rating_distribution || {})
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([star, count]) => ({ star: `${star}★`, count }));

  const aspectData = (summary.aspect_sentiments || []).map(a => ({
    aspect: a.aspect,
    positive: a.positive_count,
    negative: a.negative_count,
    neutral: a.neutral_count,
    total: a.positive_count + a.negative_count + a.neutral_count,
  }));

  const sentimentPie = aspectData.reduce(
    (acc, a) => {
      acc[0].value += a.positive;
      acc[1].value += a.negative;
      acc[2].value += a.neutral;
      return acc;
    },
    [
      { name: 'Positive', value: 0, fill: SENTIMENT_COLORS.positive },
      { name: 'Negative', value: 0, fill: SENTIMENT_COLORS.negative },
      { name: 'Neutral', value: 0, fill: SENTIMENT_COLORS.neutral },
    ]
  );

  return (
    <div className="min-h-screen bg-gray-950 pt-14">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex items-center gap-3 mb-8">
          <TrendingUp className="w-6 h-6 text-brand-400" />
          <div>
            <h1 className="text-xl font-bold text-white">{product?.name}</h1>
            <p className="text-sm text-gray-500">Analysis Dashboard · {summary.total_reviews} reviews analyzed</p>
          </div>
        </div>

        {/* Top stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Reviews', value: summary.total_reviews, color: 'text-white' },
            { label: 'Avg Rating', value: summary.avg_rating?.toFixed(1) ?? '—', color: 'text-yellow-400' },
            { label: 'Conflicts Found', value: summary.conflict_count, color: 'text-orange-400' },
            { label: 'Aspects Tracked', value: summary.aspect_sentiments?.length ?? 0, color: 'text-brand-400' },
          ].map(s => (
            <div key={s.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
              <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Rating distribution */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-gray-300 mb-4">Rating Distribution</h2>
            {ratingData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={ratingData} margin={{ left: -20 }}>
                  <XAxis dataKey="star" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                    labelStyle={{ color: '#f3f4f6' }}
                    itemStyle={{ color: '#d1d5db' }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {ratingData.map((_, i) => (
                      <Cell key={i} fill={RATING_COLORS[i] || '#8b5cf6'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="text-gray-600 text-sm text-center py-8">No rating data available.</p>}
          </div>

          {/* Sentiment pie */}
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-gray-300 mb-4">Overall Sentiment Mix</h2>
            {sentimentPie.some(s => s.value > 0) ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sentimentPie} dataKey="value" cx="50%" cy="50%" outerRadius={75} label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`} labelLine={false}>
                    {sentimentPie.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }} />
                  <Legend iconType="circle" wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <p className="text-gray-600 text-sm text-center py-8">No sentiment data available.</p>}
          </div>
        </div>

        {/* Aspect breakdown */}
        {aspectData.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5 mb-6">
            <h2 className="text-sm font-semibold text-gray-300 mb-4">Aspect Sentiment Breakdown</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={aspectData} margin={{ left: -10, bottom: 20 }}>
                <XAxis dataKey="aspect" tick={{ fill: '#9ca3af', fontSize: 11 }} angle={-30} textAnchor="end" />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }} itemStyle={{ color: '#d1d5db' }} />
                <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
                <Bar dataKey="positive" name="Positive" fill="#10b981" radius={[2, 2, 0, 0]} stackId="a" />
                <Bar dataKey="neutral" name="Neutral" fill="#6b7280" radius={[0, 0, 0, 0]} stackId="a" />
                <Bar dataKey="negative" name="Negative" fill="#ef4444" radius={[2, 2, 0, 0]} stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Aspect badges */}
        {summary.aspect_sentiments?.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
            <h2 className="text-sm font-semibold text-gray-300 mb-4">Aspect Summary</h2>
            <div className="space-y-3">
              {summary.aspect_sentiments.map(a => {
                const total = a.positive_count + a.negative_count + a.neutral_count || 1;
                const dominant = a.positive_count >= a.negative_count ? 'positive' : 'negative';
                return (
                  <div key={a.aspect} className="flex items-center gap-3">
                    <AspectBadge aspect={a.aspect} sentiment={dominant} />
                    <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden flex">
                      <div className="bg-emerald-500 h-full" style={{ width: `${(a.positive_count / total) * 100}%` }} />
                      <div className="bg-gray-600 h-full" style={{ width: `${(a.neutral_count / total) * 100}%` }} />
                      <div className="bg-red-500 h-full" style={{ width: `${(a.negative_count / total) * 100}%` }} />
                    </div>
                    <span className="text-xs text-gray-500 w-16 text-right">
                      {a.positive_count}+ {a.negative_count}−
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
