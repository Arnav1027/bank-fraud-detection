// Frontend type definitions

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'analyst' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Transaction {
  id: number;
  user_id: number;
  amount: number;
  merchant_id: string;
  merchant_category: string;
  transaction_location?: string;
  fraud_score: number;
  is_fraud: boolean;
  status: string;
  model_version?: string;
  created_at: string;
  updated_at: string;
}

export interface FraudCheckRequest {
  user_id: number;
  amount: number;
  merchant_id: string;
  merchant_category: string;
  transaction_location?: string;
  transaction_timestamp: string;
}

export interface FraudCheckResponse {
  transaction_id: number;
  fraud_score: number;
  is_fraud: boolean;
  risk_level: 'low' | 'medium' | 'high';
  recommendation: 'APPROVE' | 'REVIEW' | 'BLOCK';
  processing_time_ms?: number;
  explanation?: {
    top_features: Array<{
      name: string;
      contribution: number;
      value: number;
    }>;
    confidence: number;
    insights: string[];
    explanation_text: string;
  };
}

export interface TransactionListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Transaction[];
}

export interface FraudSummary {
  total_transactions: number;
  flagged_transactions: number;
  fraud_rate: number;
  total_amount_at_risk: number;
  avg_fraud_score: number;
  high_risk_count: number;
}

export interface FraudAlert {
  transaction_id: number;
  user_id: number;
  amount: number;
  fraud_score: number;
  merchant_id: string;
  flagged_at: string;
}

export interface AnalyticsSummaryResponse {
  summary: FraudSummary;
  top_alerts: FraudAlert[];
  daily_fraud_counts: Record<string, number>;
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  pr_auc: number;
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
  model_version: string;
}
