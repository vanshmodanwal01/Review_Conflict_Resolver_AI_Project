import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Laptop, ChevronRight, BarChart2, AlertTriangle,
  ArrowLeft, RefreshCw, CheckCircle, Clock, XCircle, Star
} from 'lucide-react';
import { getProduct, getAnalysisSummary, triggerAnalysis, getAnalysisJob, getProductReviews } from '../api/client';
import type { Product, AnalysisSummary, Review } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

type JobStatus = 'idle' | 'pending' | 'running' | 'completed' | 'failed';

export default function ProductDetailPage() {
  const { productId } = useParams<{ productId: string }>();
  const id = Number(productId);
  const navigate = useNavigate();

  const [product, setProduct] = useState<Product | null>(null);
  const [summary, setSummary] = useState<AnalysisSummary | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [jobStatus, setJobStatus] = useState<JobStatus>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    Promise.all([
      getProduct(id),
      getAnalysisSummary(id).catch(() => ({ data: null })),
      getProductReviews(id).catch(() => ({ data: [] })),
    ])
      .then(([pRes, sRes, rRes]) => {
        setProduct(pRes.data);
        setSummary(sRes.data);
        setReviews(rRes.data || []);
      })
      .catch(() => setError('Failed to load product.'))
      .finally(() => setLoading(false));
  }, [id]);

  // Poll job status
  useEffect(() => {
    if (!jobId || jobStatus === 'completed' || jobStatus === 'failed') return;
    const timer = setInterval(async () => {
      try {
        const r = await getAnalysisJob(jobId);
        const job = r.data;
        if (job.status === 'completed') {
          setJobStatus('completed');
          setStatusMsg('Analysis complete!');
          clearInterval(timer);
          // Reload summary
          const sr = await getAnalysisSummary(id);
          setSummary(sr.data);
        } else if (job.status === 'failed') {
          setJobStatus('failed');
          setStatusMsg(job.message || 'Analysis failed.');
          clearInterval(timer);
        } else {
          setStatusMsg(job.message || 'Processing…');
        }
      } catch { /* ignore */ }
    }, 2000);
    return () => clearInterval(timer);
  }, [jobId, jobStatus, id]);

  const handleAnalyze = async () => {
    setJobStatus('pending');
    setStatusMsg('Starting analysis…');
    try {
      const r = await triggerAnalysis(id);
      setJobId(r.data.job_id);
      setJobStatus('running');
      setStatusMsg('Analysis running…');
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setJobStatus('failed');
      setStatusMsg(msg || 'Failed to start analysis.');
    }
  };

  if (loading) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center"><LoadingSpinner size="lg" label="Loading product…" /></div>;
  if (error || !product) return <div className="min-h-screen bg-gray-950 pt-14 flex items-center justify-center text-red-400">{error || 'Product not found.'}</div>;

  const hasAnalysis = summary && summary.analysis_status === 'completed';

  const statusIcon = {
    idle: null,
    pending: <Clock className="w-4 h-4 text-yellow-400" />,
    running: <RefreshCw className="w-4 h-4 text-brand-400 animate-spin" />,
    completed: <CheckCircle className="w-4 h-4 text-emerald-400" />,
    failed: <XCircle className="w-4 h-4 text-red-400" />,
  }[jobStatus];

  return (
    <div className="min-h-screen bg-gray-950 pt-14">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-gray-500 hover:text-white text-sm mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        {/* Product header */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 bg-gray-800 rounded-xl flex items-center justify-center flex-shrink-0">
              <Laptop className="w-7 h-7 text-brand-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold text-white">{product.name}</h1>
              <p className="text-gray-400 text-sm mt-1">
                {product.brand} {product.model_number ? `· ${product.model_number}` : ''} · {product.category}
              </p>
              {product.description && <p className="text-gray-500 text-sm mt-2 line-clamp-3">{product.description}</p>}
            </div>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-4 mt-6 pt-5 border-t border-gray-800">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{reviews.length}</p>
              <p className="text-xs text-gray-500 mt-0.5">Reviews</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">
                {summary?.avg_rating ? summary.avg_rating.toFixed(1) : '—'}
              </p>
              <p className="text-xs text-gray-500 mt-0.5">Avg Rating</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-400">{summary?.conflict_count ?? '—'}</p>
              <p className="text-xs text-gray-500 mt-0.5">Conflicts Found</p>
            </div>
          </div>
        </div>

        {/* Analyze CTA */}
        {!hasAnalysis && (
          <div className="bg-brand-900/30 border border-brand-800 rounded-2xl p-6 mb-6 text-center">
            <BarChart2 className="w-10 h-10 text-brand-400 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-white mb-1">Run AI Analysis</h2>
            <p className="text-gray-400 text-sm mb-4">
              Identify conflicting reviews and get AI-generated explanations for why customers disagree.
            </p>
            <button
              onClick={handleAnalyze}
              disabled={jobStatus === 'pending' || jobStatus === 'running'}
              className="inline-flex items-center gap-2 px-6 py-3 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white rounded-xl font-medium transition-colors"
            >
              {statusIcon || <BarChart2 className="w-4 h-4" />}
              {jobStatus === 'idle' ? 'Start Analysis' : statusMsg}
            </button>
            {statusMsg && jobStatus !== 'running' && jobStatus !== 'pending' && (
              <p className="text-sm mt-2 text-gray-400">{statusMsg}</p>
            )}
          </div>
        )}

        {hasAnalysis && (
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            <Link
              to={`/products/${id}/dashboard`}
              className="flex-1 flex items-center justify-center gap-2 bg-gray-900 border border-gray-800 hover:border-brand-600 rounded-xl p-4 transition-colors group"
            >
              <BarChart2 className="w-5 h-5 text-brand-400" />
              <div className="text-left">
                <p className="font-medium text-white">Analysis Dashboard</p>
                <p className="text-xs text-gray-500">Sentiment & aspect breakdown</p>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-brand-400 ml-auto" />
            </Link>

            <Link
              to={`/products/${id}/conflicts`}
              className="flex-1 flex items-center justify-center gap-2 bg-gray-900 border border-gray-800 hover:border-orange-700 rounded-xl p-4 transition-colors group"
            >
              <AlertTriangle className="w-5 h-5 text-orange-400" />
              <div className="text-left">
                <p className="font-medium text-white">Conflict Explorer</p>
                <p className="text-xs text-gray-500">{summary.conflict_count} conflicts detected</p>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-orange-400 ml-auto" />
            </Link>
          </div>
        )}

        {/* Re-analyze */}
        {hasAnalysis && (
          <button
            onClick={handleAnalyze}
            disabled={jobStatus === 'pending' || jobStatus === 'running'}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors disabled:opacity-50 mb-6"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Re-run Analysis
            {statusMsg && <span className="text-brand-400 ml-1">{statusMsg}</span>}
          </button>
        )}

        {/* Recent reviews */}
        {reviews.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Sample Reviews</h2>
            <div className="space-y-3">
              {reviews.slice(0, 5).map(rev => (
                <div key={rev.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    {rev.rating && (
                      <span className="flex items-center gap-0.5 text-yellow-400 text-sm font-medium">
                        <Star className="w-3.5 h-3.5 fill-yellow-400" />{rev.rating}
                      </span>
                    )}
                    {rev.variant && <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">{rev.variant}</span>}
                    <span className="text-xs text-gray-600 ml-auto capitalize">{rev.source}</span>
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed line-clamp-3">{rev.review_text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
