import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { PredictionExplanationCard } from './PredictionExplanation';

interface Transaction {
  id: number;
  user_id: number;
  merchant_id: string;
  merchant_category: string;
  amount: number;
  fraud_score: number;
  is_fraud: boolean;
  transaction_timestamp: string;
}

interface TransactionListResponse {
  total: number;
  items: Transaction[];
}

export function TransactionHistory() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [filters, setFilters] = useState({
    isFraud: 'all',
    search: '',
  });

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 50 };

      if (filters.isFraud !== 'all') {
        params.is_fraud = filters.isFraud === 'fraud';
      }

      const response = await apiClient.listTransactions(params);
      setTransactions(response.data.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setExpandedId(null);
  };

  const getRiskBadgeColor = (score: number) => {
    if (score < 0.3) return 'bg-green-100 text-green-800';
    if (score < 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getRiskLevel = (score: number) => {
    if (score < 0.3) return 'Low';
    if (score < 0.7) return 'Medium';
    return 'High';
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString() +
      ' ' +
      new Date(timestamp).toLocaleTimeString();
  };

  const filteredTransactions = transactions.filter((t) => {
    if (filters.isFraud !== 'all') {
      const isFraudMatch = filters.isFraud === 'fraud' ? t.is_fraud : !t.is_fraud;
      if (!isFraudMatch) return false;
    }
    if (filters.search) {
      const search = filters.search.toLowerCase();
      return (
        t.merchant_id.toLowerCase().includes(search) ||
        t.merchant_category.toLowerCase().includes(search) ||
        t.amount.toString().includes(search)
      );
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-600">Loading transactions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Transaction History</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Merchant, category, amount..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.isFraud}
              onChange={(e) => handleFilterChange('isFraud', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Transactions</option>
              <option value="legitimate">Legitimate</option>
              <option value="fraud">Flagged as Fraud</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchTransactions}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-100 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Merchant
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Fraud Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Risk Level
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredTransactions.map((transaction) => (
              <React.Fragment key={transaction.id}>
                <tr className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <p className="font-medium text-gray-900">
                        {transaction.merchant_id}
                      </p>
                      <p className="text-sm text-gray-500">
                        {transaction.merchant_category}
                      </p>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-lg font-semibold text-gray-900">
                      ${transaction.amount.toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            transaction.fraud_score < 0.3
                              ? 'bg-green-500'
                              : transaction.fraud_score < 0.7
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{
                            width: `${transaction.fraud_score * 100}%`,
                          }}
                        ></div>
                      </div>
                      <span className="ml-2 text-sm font-medium text-gray-700">
                        {(transaction.fraud_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskBadgeColor(
                        transaction.fraud_score
                      )}`}
                    >
                      {getRiskLevel(transaction.fraud_score)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    {formatDate(transaction.transaction_timestamp)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button
                      onClick={() =>
                        setExpandedId(
                          expandedId === transaction.id ? null : transaction.id
                        )
                      }
                      className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                    >
                      {expandedId === transaction.id ? 'Hide' : 'Details'}
                    </button>
                  </td>
                </tr>
                {expandedId === transaction.id && (
                  <tr className="bg-blue-50">
                    <td colSpan={6} className="px-6 py-4">
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                        <div>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            Transaction ID
                          </p>
                          <p className="text-lg font-bold text-gray-900 mt-1">
                            #{transaction.id}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            User ID
                          </p>
                          <p className="text-lg font-bold text-gray-900 mt-1">
                            {transaction.user_id}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            Status
                          </p>
                          <p
                            className={`text-lg font-bold mt-1 ${
                              transaction.is_fraud
                                ? 'text-red-600'
                                : 'text-green-600'
                            }`}
                          >
                            {transaction.is_fraud ? '⚠️ Flagged' : '✅ Approved'}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            Full Score
                          </p>
                          <p className="text-lg font-bold text-gray-900 mt-1">
                            {(transaction.fraud_score * 100).toFixed(3)}%
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            Merchant ID
                          </p>
                          <p className="text-lg font-bold text-gray-900 mt-1 break-words">
                            {transaction.merchant_id}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-gray-600 uppercase">
                            Category
                          </p>
                          <p className="text-lg font-bold text-gray-900 mt-1">
                            {transaction.merchant_category}
                          </p>
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t border-blue-200">
                        <p className="text-xs font-semibold text-gray-600 uppercase">
                          Prediction Details
                        </p>
                        <p className="text-sm text-gray-700 mt-2">
                          This transaction was analyzed using machine learning models
                          and scored based on multiple features including transaction
                          amount, merchant category, time of day, and user history.
                        </p>
                      </div>
                      
                      <PredictionExplanationCard
                        fraudScore={transaction.fraud_score}
                        isFraud={transaction.is_fraud}
                        explanation={undefined}
                      />
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {filteredTransactions.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">No transactions found</p>
        </div>
      )}

      <div className="mt-6 text-sm text-gray-600">
        Showing {filteredTransactions.length} of {transactions.length} transactions
      </div>
    </div>
  );
}
