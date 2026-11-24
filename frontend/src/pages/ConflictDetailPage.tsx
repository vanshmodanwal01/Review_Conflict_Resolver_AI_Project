import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Info, ChevronDown, ChevronUp, Zap } from 'lucide-react';
import { getConflictDetail, getProductReviews } from '../api/client';
import type { ConflictGroup, Review } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import AspectBadge from '../components/AspectBadge';
import EvidenceBox from '../components/EvidenceBox';

export default function ConflictDetailPage() {
  const { productId, conflictId } = useParams<{ productId: string; conflictId: string }>();
  const navigate = useNavigate();

  const [conflict, setConflict] = useState<ConflictGroup | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAllEvidence, setShowAllEvidence] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      getConflictDetail(Number(conflictId)),
      getProductReviews(Number(productId)).catch(() => ({ data: [] })),
    ])
      .then(([c, r]) => { setConflict(c.data); setReviews(r.data || []); })
      .catch(() => setError('Failed to load conflict details.'))
      .finally(() => setLoading(false));
  }, [conflictId, productId]);

  if (loading) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center"><LoadingSpinner size="lg" /></div>;
  if (error || !conflict) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center text-red-400">{error}</div>;

  const reviewMap: Record<number, Review> = {};
  reviews.forEach(r => { reviewMap[r.id] = r; });

  const supportingEvidence = (conflict.evidence || []).filter(e => e.position === 'supporting');
  const opposingEvidence = (conflict.evidence || []).filter(e => e.position === 'opposing');
  const explanation = conflict.explanations?.[0];

  const displaySupporting = showAllEvidence ? supportingEvidence : supportingEvidence.slice(0, 2);
  const displayOpposing = showAllEvidence ? opposingEvidence : opposingEvidence.slice(0, 2);
  const hasMore = supportingEvidence.length + opposingEvidence.length > 4;

  return (
    <div className="min-h-screen bg-gray-950 pt-14">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Conflicts
        </button>

        {/* Header */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
          <div className="flex items-center gap-3 mb-3">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <AspectBadge aspect={conflict.aspect} sentiment="conflict" />
            <span className="text-xs text-gray-500 capitalize">{conflict.conflict_type.replace(/_/g, ' ')}</span>
          </div>
          {conflict.description && (
            <p className="text-gray-300 text-sm leading-relaxed">{conflict.description}</p>
          )}
          <div className="flex items-center gap-4 mt-4 text-xs text-gray-500">
            <span>Conflict score: <span className="text-orange-400 font-medium">{(conflict.conflict_score * 100).toFixed(0)}%</span></span>
            <span>{conflict.positive_count} positive · {conflict.negative_count} negative</span>
          </div>
        </div>

        {/* AI Explanation */}
        {explanation ? (
          <div className="bg-brand-900/20 border border-brand-800 rounded-2xl p-6 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-brand-400" />
              <h2 className="text-sm font-semibold text-brand-300">AI Explanation</h2>
              {explanation.confidence_score && (
                <span className="ml-auto text-xs text-gray-500">
                  Confidence: {(explanation.confidence_score * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <p className="text-gray-200 text-sm leading-relaxed">{explanation.explanation_text}</p>

            {explanation.contributing_factors && explanation.contributing_factors.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-medium text-gray-500 mb-2">Contributing Factors</p>
                <ul className="space-y-1">
                  {explanation.contributing_factors.map((f, i) => (
                    <li key={i} className="text-sm text-gray-300 flex gap-2">
                      <span className="text-brand-400 mt-0.5">•</span> {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {explanation.missing_information && explanation.missing_information.length > 0 && (
              <div className="mt-3 pt-3 border-t border-brand-800/50">
                <p className="text-xs font-medium text-gray-500 mb-1">Information gaps</p>
                <ul className="space-y-0.5">
                  {explanation.missing_information.map((m, i) => (
                    <li key={i} className="text-xs text-gray-500 flex gap-2">
                      <span className="text-gray-600">–</span> {m}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {explanation.provider_used && (
              <p className="text-xs text-gray-600 mt-3 capitalize">Generated by {explanation.provider_used}</p>
            )}
          </div>
        ) : (
          <div className="bg-gray-900 border border-dashed border-gray-700 rounded-2xl p-5 mb-6 flex items-center gap-3 text-gray-500 text-sm">
            <Info className="w-4 h-4 flex-shrink-0" />
            No AI explanation available. Ensure a Gemini or OpenAI API key is configured.
          </div>
        )}

        {/* Evidence */}
        {(conflict.evidence || []).length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-400 mb-3">Review Evidence</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div className="space-y-3">
                <p className="text-xs text-emerald-500 font-medium uppercase tracking-wider">Positive ({supportingEvidence.length})</p>
                {displaySupporting.map(ev => {
                  const rev = reviewMap[ev.review_id];
                  return (
                    <EvidenceBox
                      key={ev.id}
                      text={ev.evidence_text}
                      position="supporting"
                      source={rev?.source}
                      rating={rev?.rating}
                    />
                  );
                })}
                {displaySupporting.length === 0 && <p className="text-xs text-gray-600">None</p>}
              </div>
              <div className="space-y-3">
                <p className="text-xs text-red-500 font-medium uppercase tracking-wider">Negative ({opposingEvidence.length})</p>
                {displayOpposing.map(ev => {
                  const rev = reviewMap[ev.review_id];
                  return (
                    <EvidenceBox
                      key={ev.id}
                      text={ev.evidence_text}
                      position="opposing"
                      source={rev?.source}
                      rating={rev?.rating}
                    />
                  );
                })}
                {displayOpposing.length === 0 && <p className="text-xs text-gray-600">None</p>}
              </div>
            </div>
            {hasMore && (
              <button
                onClick={() => setShowAllEvidence(v => !v)}
                className="flex items-center gap-1 text-sm text-gray-500 hover:text-white transition-colors"
              >
                {showAllEvidence ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                {showAllEvidence ? 'Show less' : 'Show all evidence'}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
