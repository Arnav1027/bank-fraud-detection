import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuth } from './hooks/useApi';
import { LoginPage } from './components/LoginPage';
import { Dashboard } from './components/Dashboard';
import { TransactionChecker } from './components/TransactionChecker';
import { TransactionHistory } from './components/TransactionHistory';
import { BatchUpload } from './components/BatchUpload';
import './index.css';

function App() {
  const { user, logout } = useAuth();

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {user && <Navbar user={user} onLogout={logout} />}
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={user ? <Dashboard /> : <Navigate to="/login" />}
          />
          <Route
            path="/check"
            element={user ? <TransactionChecker /> : <Navigate to="/login" />}
          />
          <Route
            path="/transactions"
            element={user ? <TransactionHistory /> : <Navigate to="/login" />}
          />
          <Route
            path="/batch"
            element={user ? <BatchUpload /> : <Navigate to="/login" />}
          />
          <Route
            path="/"
            element={user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />}
          />
        </Routes>
      </div>
    </Router>
  );
}

interface NavbarProps {
  user: any;
  onLogout: () => void;
}

function Navbar({ user, onLogout }: NavbarProps) {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link to="/dashboard" className="text-xl font-bold">
            🚨 Fraud Detection
          </Link>
          <div className="hidden md:flex space-x-4">
            <Link to="/dashboard" className="hover:bg-blue-700 px-3 py-2 rounded">
              Dashboard
            </Link>
            <Link to="/transactions" className="hover:bg-blue-700 px-3 py-2 rounded">
              Transactions
            </Link>
            <Link to="/check" className="hover:bg-blue-700 px-3 py-2 rounded">
              Check Transaction
            </Link>
            <Link to="/batch" className="hover:bg-blue-700 px-3 py-2 rounded">
              Batch Upload
            </Link>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className="text-sm">{user?.full_name}</span>
          <button
            onClick={onLogout}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default App;
