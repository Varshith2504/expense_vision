import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  FileSpreadsheet, 
  Settings, 
  RefreshCw
} from 'lucide-react';
import Dashboard from './components/Dashboard';
import ClaimsTable from './components/ClaimsTable';
import ClaimDetailModal from './components/ClaimDetailModal';
import PolicyConfig from './components/PolicyConfig';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(true);

  // Global Compliance Policies (INR)
  const [policies, setPolicies] = useState({
    internLimit: 3000.0,
    travelCap: 1500.0,
    itBudget: 50000.0
  });

  // Global Claims Database
  const [claims, setClaims] = useState([]);

  // Fetch claims and policies on mount
  const fetchBackendData = async () => {
    setIsLoading(true);
    try {
      // 1. Fetch claims
      const claimsRes = await fetch('/api/claims');
      if (claimsRes.ok) {
        const claimsData = await claimsRes.json();
        setClaims(claimsData);
        setBackendOnline(true);
      } else {
        setBackendOnline(false);
      }

      // 2. Fetch policies
      const policiesRes = await fetch('/api/policies');
      if (policiesRes.ok) {
        const policiesData = await policiesRes.json();
        setPolicies(policiesData);
      }
    } catch (err) {
      console.warn("Backend connection offline, using state cache:", err);
      setBackendOnline(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBackendData();
  }, []);

  // Approve claim via backend API
  const handleApproveClaim = async (id) => {
    try {
      const res = await fetch(`/api/claims/${id}/approve`, { method: 'POST' });
      if (res.ok) {
        const updated = await res.json();
        setClaims(prev => prev.map(c => c.id === id ? updated : c));
      } else {
        setClaims(prev => prev.map(c => c.id === id ? { ...c, status: 'Approved' } : c));
      }
    } catch (err) {
      setClaims(prev => prev.map(c => c.id === id ? { ...c, status: 'Approved' } : c));
    }
  };

  // Reject claim via backend API
  const handleRejectClaim = async (id) => {
    try {
      const res = await fetch(`/api/claims/${id}/reject`, { method: 'POST' });
      if (res.ok) {
        const updated = await res.json();
        setClaims(prev => prev.map(c => c.id === id ? updated : c));
      } else {
        setClaims(prev => prev.map(c => c.id === id ? { ...c, status: 'Rejected' } : c));
      }
    } catch (err) {
      setClaims(prev => prev.map(c => c.id === id ? { ...c, status: 'Rejected' } : c));
    }
  };

  // Update compliance policies dynamically via backend API
  const handleUpdatePolicies = async (newPolicies) => {
    setPolicies(newPolicies);
    try {
      const res = await fetch('/api/policies', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPolicies)
      });
      if (res.ok) {
        fetchBackendData();
      }
    } catch (err) {
      console.warn("Failed to sync policies with backend:", err);
    }
  };

  const getPageTitle = () => {
    switch (activeTab) {
      case 'claims':
        return 'Expense Claims Audit';
      case 'policies':
        return 'Policy & Rules Settings';
      default:
        return 'Dashboard Overview';
    }
  };

  const getPageSubtitle = () => {
    switch (activeTab) {
      case 'claims':
        return 'Verify claims, inspect receipt scans, check for edits, and approve or reject submissions';
      case 'policies':
        return 'Adjust bill limits, travel caps, and department budgets';
      default:
        return 'Real-time overview of active claims, fraud warning flags, and spending reports';
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <div className={`sidebar ${isSidebarOpen ? '' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="project-title-area">
            <h1 className="project-title">Expense Vision</h1>
          </div>
          <p className="project-subtitle">FastAPI + React Audit Portal</p>
        </div>

        <ul className="sidebar-menu">
          <li 
            className={`menu-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} />
            Dashboard Overview
          </li>
          <li 
            className={`menu-item ${activeTab === 'claims' ? 'active' : ''}`}
            onClick={() => setActiveTab('claims')}
          >
            <FileSpreadsheet size={18} />
            Claims Explorer
          </li>
          <li 
            className={`menu-item ${activeTab === 'policies' ? 'active' : ''}`}
            onClick={() => setActiveTab('policies')}
          >
            <Settings size={18} />
            Policy Settings
          </li>
        </ul>

        <div className="sidebar-footer">
          <div>Python Backend Status:</div>
          <div style={{ fontWeight: 600, color: backendOnline ? '#4ade80' : '#f87171', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '6px', justifyContent: 'center' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: backendOnline ? '#4ade80' : '#f87171' }}></span>
            {backendOnline ? 'FastAPI Online' : 'Connecting...'}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Navbar */}
        <header className="navbar">
          <div className="nav-title-section">
            <h1>{getPageTitle()}</h1>
            <p>{getPageSubtitle()}</p>
          </div>
          
          <div className="nav-profile">
            <button 
              onClick={fetchBackendData}
              className="view-action-btn"
              title="Refresh Claims Data"
              style={{ marginRight: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <RefreshCw size={14} className={isLoading ? 'spin' : ''} /> Sync Claims
            </button>
            <div className="user-badge">
              <span className="user-name">Finance Manager</span>
              <span className="user-role" style={{ display: 'block' }}>Administrator Account</span>
            </div>
            <div className="university-logo-placeholder">AD</div>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {activeTab === 'dashboard' && (
            <Dashboard 
              claims={claims} 
              onNavigate={setActiveTab} 
              policies={policies}
            />
          )}

          {activeTab === 'claims' && (
            <ClaimsTable 
              claims={claims} 
              onViewClaim={(claim) => setSelectedClaim(claim)} 
            />
          )}

          {activeTab === 'policies' && (
            <PolicyConfig 
              policies={policies} 
              onUpdatePolicies={handleUpdatePolicies} 
            />
          )}
        </main>
      </div>

      {/* Detail Slide-in Panel */}
      <ClaimDetailModal 
        claim={selectedClaim} 
        isOpen={selectedClaim !== null} 
        onClose={() => setSelectedClaim(null)}
        onApprove={handleApproveClaim}
        onReject={handleRejectClaim}
      />
    </div>
  );
}
