export interface Product {
  id: number;
  name: string;
  brand?: string;
  model_number?: string;
  category: string;
  subcategory?: string;
  description?: string;
  image_url?: string;
  created_at: string;
}

export interface Review {
  id: number;
  product_id: number;
  source: string;
  rating?: number;
  review_text: string;
  variant?: string;
  review_date?: string;
  created_at: string;
}

export interface AspectSentiment {
  aspect: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  avg_sentiment_score: number;
}

export interface AnalysisSummary {
  product_id: number;
  product_name: string;
  total_reviews: number;
  avg_rating: number;
  rating_distribution: Record<string, number>;
  aspect_sentiments: AspectSentiment[];
  conflict_count: number;
  analysis_status: string;
  last_analyzed?: string;
}

export interface ConflictEvidence {
  id: number;
  review_id: number;
  evidence_text: string;
  position: string;
  sentiment_score: number;
  review?: Review;
}

export interface AIExplanation {
  id: number;
  explanation_text: string;
  confidence_score?: number;
  provider_used?: string;
  contributing_factors?: string[];
  missing_information?: string[];
  generated_at: string;
}

export interface ConflictGroup {
  id: number;
  product_id: number;
  aspect: string;
  conflict_type: string;
  conflict_score: number;
  description?: string;
  positive_count: number;
  negative_count: number;
  created_at: string;
  evidence?: ConflictEvidence[];
  explanations?: AIExplanation[];
}

export interface PersonalizedInsight {
  use_case: string;
  usage_intensity: string;
  variant?: string;
  recommendation: string;
  relevant_conflicts: ConflictGroup[];
  advice: string[];
  confidence: string;
}

export interface AnalysisJob {
  job_id: string;
  product_id: number;
  status: string;
  progress?: number;
  message?: string;
  created_at: string;
  completed_at?: string;
}
