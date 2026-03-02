import React from 'react';

interface TopFeature {
  name: string;
  contribution: number;
  value: number;
}

interface PredictionExplanation {
  top_features: TopFeature[];
  confidence: number;
  insights: string[];
  explanation_text: string;
}

interface PredictionExplanationProps {
  explanation?: PredictionExplanation;
  fraudScore: number;
  isFraud: boolean;
}

export function PredictionExplanationCard({
  explanation,
  fraudScore,
  isFraud,
}: PredictionExplanationProps) {
  if (!explanation) {
    return null;
  }

  const getContributionColor = (contribution: number): string => {
    if (contribution > 30) return 'bg-red-100';
    if (contribution > 15) return 'bg-orange-100';
    return 'bg-yellow-100';
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence > 80) return 'text-green-700 bg-green-50';
    if (confidence > 60) return 'text-blue-700 bg-blue-50';
    return 'text-orange-700 bg-orange-50';
  };

  return (
    <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-6 border border-indigo-200 mt-6">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">💡 Prediction Explanation</h3>
        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getConfidenceColor(explanation.confidence)}`}>
          {explanation.confidence.toFixed(0)}% Confidence
        </div>
      </div>

      {/* Explanation Text */}
      <p className="text-gray-700 mb-4 leading-relaxed italic">
        {`"${explanation.explanation_text}"`}
      </p>

      {/* Feature Contributions */}
      {explanation.top_features && explanation.top_features.length > 0 && (
        <div className="mb-6">
          <h4 className="font-semibold text-gray-900 mb-3">Top Contributing Factors:</h4>
          <div className="space-y-2">
            {explanation.top_features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div className="w-24 text-sm font-medium text-gray-700 truncate">
                  {feature.name}
                </div>
                <div className="flex-1">
                  <div className="h-6 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full flex items-center justify-center text-xs font-bold text-gray-900 transition-all ${getContributionColor(
                        feature.contribution
                      )}`}
                      style={{ width: `${Math.max(feature.contribution, 5)}%` }}
                    >
                      {feature.contribution > 8 && `${feature.contribution.toFixed(1)}%`}
                    </div>
                  </div>
                </div>
                <div className="w-20 text-right text-sm text-gray-600">
                  {feature.contribution.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Insights */}
      {explanation.insights && explanation.insights.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-indigo-100">
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <span>📊</span> Key Insights
          </h4>
          <ul className="space-y-1">
            {explanation.insights.map((insight, idx) => (
              <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-indigo-500 mt-1">•</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Risk Assessment Summary */}
      <div className="mt-4 pt-4 border-t border-indigo-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase">Fraud Score</p>
            <p className={`text-2xl font-bold mt-1 ${
              fraudScore > 0.7 ? 'text-red-600' : fraudScore > 0.3 ? 'text-yellow-600' : 'text-green-600'
            }`}>
              {(fraudScore * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase">Risk Level</p>
            <p className={`text-2xl font-bold mt-1 ${
              fraudScore < 0.3 ? 'text-green-600' : fraudScore < 0.7 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {fraudScore < 0.3 ? '🟢 Low' : fraudScore < 0.7 ? '🟡 Medium' : '🔴 High'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 font-semibold uppercase">Status</p>
            <p className={`text-2xl font-bold mt-1 ${
              isFraud ? 'text-red-600' : 'text-green-600'
            }`}>
              {isFraud ? '⚠️ Flag' : '✅ OK'}
            </p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="text-xs text-gray-600 mt-4 italic">
        This explanation is generated by machine learning models and should be used as a tool for decision support, not as the sole basis for action.
      </p>
    </div>
  );
}
