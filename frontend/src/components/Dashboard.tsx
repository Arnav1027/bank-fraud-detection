import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import apiClient from '../services/api';
import { useFetch } from '../hooks/useApi';
import { AnalyticsSummaryResponse } from '../types';
import { FraudTrendsChart } from './FraudTrendsChart';

export function Dashboard() {
  const { data: analyticsData, loading, error } = useFetch<AnalyticsSummaryResponse>(
    () => apiClient.getSummary(7),
    []
  );

  if (loading) {
    return <div className="flex items-center justify-center h-96 text-gray-600">Loading dashboard data...</div>;
  }

  if (error) {
    return (
      <div className="p-6 bg-gray-50 min-h-screen">
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <p className="text-red-800 font-semibold">Failed to load dashboard</p>
          <p className="text-red-700 text-sm mt-1">{error}</p>
          <p className="text-red-600 text-xs mt-2">Make sure you are logged in and the backend is running on port 7777</p>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return <div className="p-6">No data available</div>;
  }

  const { summary, daily_fraud_counts, top_alerts } = analyticsData;

  // Prepare chart data
  const dailyChartData = Object.entries(daily_fraud_counts).map(([date, count]) => ({
    date,
    frauds: count,
    fraudRate: summary.total_transactions > 0 ? (count / summary.total_transactions) * 100 : 0,
  }));

  const confusionData = [
    { name: 'Legitimate', value: summary.total_transactions - summary.flagged_transactions },
    { name: 'Fraudulent', value: summary.flagged_transactions },
  ];

  const COLORS = ['#10b981', '#ef4444'];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <SummaryCard
          title="Total Transactions"
          value={summary.total_transactions}
          color="blue"
        />
        <SummaryCard
          title="Fraud Rate"
          value={`${(summary.fraud_rate * 100).toFixed(2)}%`}
          color="red"
        />
        <SummaryCard
          title="Flagged Transactions"
          value={summary.flagged_transactions}
          color="yellow"
        />
        <SummaryCard
          title="Amount at Risk"
          value={`$${summary.total_amount_at_risk.toLocaleString()}`}
          color="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 mb-8">
        {/* Enhanced Fraud Trends Chart */}
        <FraudTrendsChart data={dailyChartData} title="Fraud Detection Trends (Last 7 Days)" />

        {/* Traditional Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Fraud Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Daily Fraud Count</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="frauds" fill="#ef4444" name="Frauds Detected" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Transaction Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Transaction Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={confusionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {COLORS.map((color, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent High-Risk Alerts</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                  Transaction ID
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                  Fraud Score
                </th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-900">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {top_alerts.map((alert) => (
                <tr key={alert.transaction_id} className="border-t border-gray-200 hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{alert.transaction_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">${alert.amount.toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className="px-3 py-1 text-xs font-medium text-white bg-red-600 rounded-full">
                      {(alert.fraud_score * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className="px-3 py-1 text-xs font-medium text-white bg-red-600 rounded-full">
                      BLOCKED
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

interface SummaryCardProps {
  title: string;
  value: string | number;
  color: 'blue' | 'red' | 'yellow' | 'orange';
}

function SummaryCard({ title, value, color }: SummaryCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 border-l-4 border-blue-500',
    red: 'bg-red-50 border-l-4 border-red-500',
    yellow: 'bg-yellow-50 border-l-4 border-yellow-500',
    orange: 'bg-orange-50 border-l-4 border-orange-500',
  };

  const textClasses = {
    blue: 'text-blue-900',
    red: 'text-red-900',
    yellow: 'text-yellow-900',
    orange: 'text-orange-900',
  };

  return (
    <div className={`rounded-lg shadow p-6 ${colorClasses[color]}`}>
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className={`text-2xl font-bold mt-2 ${textClasses[color]}`}>{value}</p>
    </div>
  );
}
