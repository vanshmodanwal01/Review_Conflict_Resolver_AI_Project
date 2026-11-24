import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Zap, Info } from 'lucide-react';
import { getPersonalizedInsights } from '../api/client';
import type { PersonalizedInsight } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

const USE_CASES = ['casual_browsing', 'office_work', 'content_creation', 'gaming', 'programming', 'video_editing', 'student'];
const INTENSITIES = ['low', 'medium', 'high'];
const VARIANTS = ['8GB RAM', '16GB RAM', '32GB RAM', 'Base model', 'Pro model', 'Entry level'];

export default function PersonalizedInsightsPage() {
  const { productId } = useParams<{ productId: string }>();
  const id = Number(productId);
  const navigate = useNavigate();

  const [useCase, setUseCase] = useState('');
  const [intensity, setIntensity] = useState('');
  const [variant, setVariant] = useState('');
  const [insight, setInsight] = useState<PersonalizedInsight | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!useCase) return;
    setLoading(true);
    setError('');
    setInsight(null);
    try {
      const r = await getPersonalizedInsights({
        product_id: id,
        use_case: useCase || undefined,
        usage_intensity: intensity || undefined,
        variant: variant || undefined,
      });
      setInsight(r.data);
    } catch {
      setError('Could not load personalized insights. Ensure analysis has been run.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 pt-14">
      <div className="max-w-2xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex items-center gap-3 mb-2">
          <User className="w-6 h-6 text-brand-400" />
          <h1 className="text-xl font-bold text-white">Personalized Insights</h1>
        </div>
        <p className="text-gray-500 text-sm mb-8">
          Tell us your use case and we'll filter the conflicts that matter most to you.
        </p>

        <form onSubmit={handleSubmit} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Your primary use case *</label>
            <div className="flex flex-wrap gap-2">
              {USE_CASES.map(uc => (
                <button
                  type="button"
                  key={uc}
                  onClick={() => setUseCase(uc)}
                  className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-colors border ${
                    useCase === uc
                      ? 'bg-brand-700 border-brand-500 text-white'
                      : 'border-gray-700 text-gray-400 hover:border-gray-500 hover:text-white'
                  }`}
                >
                  {uc.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Usage intensity</label>
            <div className="flex gap-2">
              {INTENSITIES.map(i => (
                <button
                  type="button"
                  key={i}
                  onClick={() => setIntensity(i)}
                  className={`flex-1 py-2 rounded-lg text-sm capitalize transition-colors border ${
                    intensity === i
                      ? 'bg-brand-700 border-brand-500 text-white'
                      : 'border-gray-700 text-gray-400 hover:border-gray-500 hover:text-white'
                  }`}
                >
                  {i}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Specific variant <span className="text-gray-600 font-normal">(optional)</span></label>
            <div className="flex flex-wrap gap-2">
              {VARIANTS.map(v => (
                <button
                  type="button"
                  key={v}
                  onClick={() => setVariant(variant === v ? '' : v)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors border ${
                    variant === v
                      ? 'bg-brand-700 border-brand-500 text-white'
                      : 'border-gray-700 text-gray-400 hover:border-gray-500 hover:text-white'
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={!useCase || loading}
            className="w-full py-3 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
          >
            {loading ? <LoadingSpinner size="sm" /> : <Zap className="w-4 h-4" />}
            {loading ? 'Analyzing…' : 'Get Personalized Insights'}
          </button>
        </form>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {insight && (
          <div className="space-y-5">
            {/* Recommendation */}
            <div className="bg-brand-900/20 border border-brand-800 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-4 h-4 text-brand-400" />
                <h2 className="font-semibold text-brand-300 text-sm">Recommendation</h2>
                <span className="ml-auto text-xs text-gray-500 capitalize">{insight.confidence} confidence</span>
              </div>
              <p className="text-gray-200 text-sm leading-relaxed">{insight.recommendation}</p>
            </div>

            {/* Advice points */}
            {insight.advice?.length > 0 && (
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-5">
                <h2 className="text-sm font-semibold text-gray-300 mb-3">Key Considerations</h2>
                <ul className="space-y-2">
                  {insight.advice.map((a, i) => (
                    <li key={i} className="flex gap-2 text-sm text-gray-300">
                      <span className="text-brand-400 font-bold mt-0.5">·</span> {a}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Relevant conflicts */}
            {insight.relevant_conflicts?.length > 0 && (
              <div>
                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Conflicts Relevant to You</h2>
                <div className="space-y-3">
                  {insight.relevant_conflicts.map((c) => (
                    <div key={c.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs bg-orange-900/50 border border-orange-700 text-orange-300 px-2 py-0.5 rounded-full capitalize">{c.aspect}</span>
                        <span className="text-xs text-gray-500">Score: {(c.conflict_score * 100).toFixed(0)}%</span>
                      </div>
                      {c.description && <p className="text-sm text-gray-400">{c.description}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {insight.relevant_conflicts?.length === 0 && (
              <div className="flex items-center gap-2 text-sm text-gray-500 bg-gray-900 border border-gray-800 rounded-xl p-4">
                <Info className="w-4 h-4" />
                No specific conflicts found for your use case. This product looks generally suitable for you.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
