import React, { useState } from 'react';
import apiClient from '../services/api';

interface BatchResult {
  records_processed: number;
  fraud_count: number;
  csv_data: string;
}

export function BatchUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BatchResult | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const droppedFile = files[0];
      if (droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile);
        setError(null);
      } else {
        setError('Please drop a CSV file');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      setFile(files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.batchCheckFraud(file);
      setResult(response.data);
      setFile(null);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to process file'
      );
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const downloadResults = () => {
    if (!result) return;

    const element = document.createElement('a');
    const csvContent = result.csv_data;
    element.setAttribute(
      'href',
      'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent)
    );
    element.setAttribute(
      'download',
      `fraud-analysis-${new Date().toISOString().split('T')[0]}.csv`
    );
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadTemplate = () => {
    const headers = [
      'user_id',
      'amount',
      'merchant_id',
      'merchant_category',
      'transaction_location',
      'transaction_timestamp',
    ];
    const sampleData = [
      [
        '1',
        '150.50',
        'AMZN001',
        'Electronics',
        'New York',
        '2026-02-28T10:30:00Z',
      ],
      [
        '2',
        '75.00',
        'STARBUCKS',
        'Coffee Shop',
        'Boston',
        '2026-02-28T14:15:00Z',
      ],
      [
        '1',
        '2500.00',
        'JEWELRY001',
        'Jewelry',
        'Miami',
        '2026-02-28T22:45:00Z',
      ],
    ];

    const csvContent = [
      headers.join(','),
      ...sampleData.map((row) => row.join(',')),
    ].join('\n');

    const element = document.createElement('a');
    element.setAttribute(
      'href',
      'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent)
    );
    element.setAttribute('download', 'sample_transactions.csv');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Batch Fraud Analysis</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload CSV</h2>

            {/* Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-900">
                <strong>Required Columns:</strong> user_id, amount, merchant_id,
                merchant_category, transaction_timestamp
              </p>
              <p className="text-sm text-blue-900 mt-2">
                <strong>Optional:</strong> transaction_location
              </p>
            </div>

            {/* File Input */}
            <form onSubmit={handleSubmit}>
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 bg-gray-50 hover:border-gray-400'
                }`}
              >
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20a4 4 0 004 4h24a4 4 0 004-4V20m-12-6l-6-6m6 6v20"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <p className="mt-2 text-lg text-gray-900 font-medium">
                  {file ? file.name : 'Drag and drop your CSV file here'}
                </p>
                <p className="text-sm text-gray-600">or click to select</p>

                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
              </div>

              {error && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Buttons */}
              <div className="mt-6 flex gap-3">
                <button
                  type="submit"
                  disabled={!file || loading}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  {loading ? 'Processing...' : 'Analyze Transactions'}
                </button>
                <button
                  type="button"
                  onClick={downloadTemplate}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition"
                >
                  Download Template
                </button>
              </div>
            </form>
          </div>

          {/* Results */}
          {result && (
            <div className="bg-white rounded-lg shadow p-6 mt-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Results</h2>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Records Processed</p>
                  <p className="text-3xl font-bold text-blue-600 mt-1">
                    {result.records_processed}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Fraud Detected</p>
                  <p className="text-3xl font-bold text-red-600 mt-1">
                    {result.fraud_count}
                  </p>
                </div>
              </div>

              <button
                onClick={downloadResults}
                className="w-full px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition"
              >
                📥 Download Results
              </button>
            </div>
          )}
        </div>

        {/* Info Sidebar */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">How to Use</h3>

          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">1. Prepare Data</h4>
              <p className="text-sm text-gray-600">
                Create a CSV file with transaction data. Use the template to get
                started.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">2. Upload File</h4>
              <p className="text-sm text-gray-600">
                Drag and drop your CSV file or click to browse. Supports files
                up to 10MB.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                3. View Results
              </h4>
              <p className="text-sm text-gray-600">
                See detailed fraud analysis and download results as CSV.
              </p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">CSV Format</h3>
            <code className="text-xs bg-gray-100 rounded p-3 block overflow-auto max-h-48 text-gray-800">
              {`user_id,amount,merchant_id,merchant_category,transaction_timestamp
1,150.50,AMZN001,Electronics,2026-02-28T10:30:00Z
2,75.00,STARBUCKS,Coffee,2026-02-28T14:15:00Z`}
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
