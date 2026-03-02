import React, { useState } from 'react';
import apiClient from '../services/api';
import { FraudCheckRequest, FraudCheckResponse } from '../types';
import { PredictionExplanationCard } from './PredictionExplanation';

export function TransactionChecker() {
  const [formData, setFormData] = useState<FraudCheckRequest>({
    user_id: 1,
    amount: 0,
    merchant_id: '',
    merchant_category: 'grocery',
    transaction_timestamp: new Date().toISOString(),
  });

  const [result, setResult] = useState<FraudCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'amount' || name === 'user_id' ? parseFloat(value) : value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await apiClient.checkFraud(formData);
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to check transaction');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600 bg-green-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'high':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Real-Time Fraud Check</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-8 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-700 font-medium mb-2">User ID</label>
            <input
              type="number"
              name="user_id"
              value={formData.user_id}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Amount</label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              step="0.01"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Merchant ID</label>
            <input
              type="text"
              name="merchant_id"
              value={formData.merchant_id}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-medium mb-2">Category</label>
            <select
              name="merchant_category"
              value={formData.merchant_category}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="grocery">Grocery</option>
              <option value="gas_station">Gas Station</option>
              <option value="restaurant">Restaurant</option>
              <option value="online">Online</option>
              <option value="entertainment">Entertainment</option>
              <option value="travel">Travel</option>
            </select>
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-gray-700 font-medium mb-2">Location</label>
          <input
            type="text"
            name="transaction_location"
            value={formData.transaction_location || ''}
            onChange={handleInputChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            placeholder="e.g., New York"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white font-medium py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Checking...' : 'Check Transaction'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg mb-8">
          {error}
        </div>
      )}

      {result && (
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Result</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-50 rounded-lg p-6">
              <p className="text-gray-600 font-medium mb-2">Fraud Score</p>
              <p className="text-4xl font-bold text-gray-900">
                {(result.fraud_score * 100).toFixed(1)}%
              </p>
            </div>

            <div className={`${getRiskColor(result.risk_level)} rounded-lg p-6`}>
              <p className="font-medium mb-2">Risk Level</p>
              <p className="text-3xl font-bold capitalize">{result.risk_level}</p>
            </div>
          </div>

          <div className="border-t pt-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600 font-medium">Status:</span>
              <span className={`px-4 py-2 rounded-full font-medium ${
                result.is_fraud ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
              }`}>
                {result.is_fraud ? 'BLOCKED' : 'APPROVED'}
              </span>
            </div>

            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600 font-medium">Recommendation:</span>
              <span className="font-medium text-gray-900">{result.recommendation}</span>
            </div>
          </div>

          <PredictionExplanationCard
            fraudScore={result.fraud_score}
            isFraud={result.is_fraud}
            explanation={result.explanation}
          />
        </div>
      )}
    </div>
  );
}
