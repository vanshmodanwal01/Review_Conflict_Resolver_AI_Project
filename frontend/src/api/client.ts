import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// ---- Products ----
export const searchProducts = (query: string, category?: string) =>
  api.get('/products/search', { params: { q: query, category } });

export const getProduct = (productId: number) =>
  api.get(`/products/${productId}`);

export const listProducts = (skip = 0, limit = 20) =>
  api.get('/products/', { params: { skip, limit } });

// ---- Reviews ----
export const getProductReviews = (productId: number, skip = 0, limit = 50) =>
  api.get('/reviews/', { params: { product_id: productId, skip, limit } });

// ---- Analysis ----
export const triggerAnalysis = (productId: number) =>
  api.post(`/analysis/${productId}`);

export const getAnalysisJob = (jobId: string) =>
  api.get(`/analysis/job/${jobId}`);

export const getAnalysisSummary = (productId: number) =>
  api.get(`/analysis/summary/${productId}`);

// ---- Conflicts ----
export const getConflicts = (productId: number) =>
  api.get('/conflicts/', { params: { product_id: productId } });

export const getConflictDetail = (conflictId: number) =>
  api.get(`/conflicts/${conflictId}`);

// ---- Insights ----
export const getPersonalizedInsights = (params: {
  product_id: number;
  use_case?: string;
  usage_intensity?: string;
  variant?: string;
}) => api.get('/insights/personalized', { params });
