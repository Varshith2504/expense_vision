import React from 'react';
import { DollarSign, Clock, AlertTriangle, ShieldCheck, TrendingUp, Award, HelpCircle } from 'lucide-react';

export default function Dashboard({ claims, onNavigate, policies }) {
  // Calculate metrics
  const totalReimbursed = claims
    .filter(c => c.status === 'Approved')
    .reduce((sum, c) => sum + c.amount, 0);

  const pendingClaimsCount = claims.filter(c => c.status === 'Pending').length;
  
  const highRiskCount = claims.filter(c => c.riskLevel === 'High' && c.status === 'Pending').length;

  const policyViolationsCount = claims.filter(c => {
    if (c.status !== 'Pending') return false;
    const failedChecks = Object.values(c.policyChecks || {}).filter(check => !check.passed).length;
    return failedChecks > 0;
  }).length;

  // Monthly stats
  const monthlyStats = [
    { month: 'Feb', amount: 35000, risk: 2 },
    { month: 'Mar', amount: 52000, risk: 1 },
    { month: 'Apr', amount: 41000, risk: 0 },
    { month: 'May', amount: 75000, risk: 3 },
    { month: 'Jun', amount: 62000, risk: 1 },
    { month: 'Jul', amount: claims.reduce((sum, c) => sum + c.amount, 0), risk: claims.filter(c => c.riskLevel === 'High').length }
  ];

  // Category breakdown
  const categories = claims.reduce((acc, c) => {
    acc[c.category] = (acc[c.category] || 0) + c.amount;
    return acc;
  }, {});

  const categoryList = Object.keys(categories).map(cat => ({
    name: cat,
    value: categories[cat],
    color: cat === 'Lab Equipment' ? '#1e3a8a' : cat === 'Travel' ? '#06b6d4' : cat === 'Food & Beverage' ? '#f59e0b' : '#a6192e'
  })).sort((a,b) => b.value - a.value);

  // Maximum value for bar scaling
  const maxAmount = Math.max(...monthlyStats.map(s => s.amount), 1000);

  // Recent warnings
  const recentAlerts = claims
    .filter(c => c.riskLevel === 'High' || Object.values(c.policyChecks || {}).some(k => !k.passed))
    .slice(0, 4);

  return (
    <div>
      {/* Corporate Overview Banner */}
      <div className="academic-header-block">
        <h2 className="academic-header-title">Expense Vision: AI-Powered Expense & Fraud Audit Portal</h2>
        <p className="academic-header-desc">
          Automate claim verification and flag digital receipt tampering in real-time. Employee receipt submissions 
          through <strong>WhatsApp (via Twilio Webhook)</strong> are parsed instantly using OCR, cross-verified with company policy rules, 
          and audited for pixel edits using Error Level Analysis.
        </p>
        <div className="academic-meta-tags">
          <div className="academic-tag">
            <ShieldCheck size={14} /> OCR Receipt Parsing
          </div>
          <div className="academic-tag">
            <AlertTriangle size={14} /> Image Manipulation Detection
          </div>
          <div className="academic-tag">
            <TrendingUp size={14} /> Outlier Risk Scoring
          </div>
          <div className="academic-tag">
            <Clock size={14} /> Real-time WhatsApp Ingestion
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-info">
            <span className="metric-label">Total Approved</span>
            <span className="metric-value">₹{totalReimbursed.toLocaleString('en-IN')}</span>
            <span className="metric-change positive">
              <TrendingUp size={14} /> Audited & Verified
            </span>
          </div>
          <div className="metric-icon-box emerald">
            <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>₹</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-info">
            <span className="metric-label">Pending Audit</span>
            <span className="metric-value">{pendingClaimsCount}</span>
            <span className="metric-change neutral">Requires review</span>
          </div>
          <div className="metric-icon-box amber">
            <Clock size={24} />
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-info">
            <span className="metric-label">High Risk Warnings</span>
            <span className="metric-value">{highRiskCount}</span>
            <span className="metric-change negative">
              {highRiskCount > 0 ? 'Requires attention' : 'No urgent alerts'}
            </span>
          </div>
          <div className="metric-icon-box rose">
            <AlertTriangle size={24} />
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-info">
            <span className="metric-label">Policy Violations</span>
            <span className="metric-value">{policyViolationsCount}</span>
            <span className="metric-change negative">Exceeded claim limits</span>
          </div>
          <div className="metric-icon-box blue">
            <ShieldCheck size={24} />
          </div>
        </div>
      </div>

      {/* Visual Charts section */}
      <div className="dashboard-details-row">
        {/* Monthly Trend bar chart */}
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h3 className="dashboard-card-title">
              <TrendingUp size={18} /> Monthly Claim Volume & Alert Rate
            </h3>
            <span className="user-role">Values in Indian Rupees (₹)</span>
          </div>
          
          <div className="chart-container">
            {monthlyStats.map((stat, idx) => {
              const heightPct = (stat.amount / maxAmount) * 80 + 10;
              return (
                <div key={idx} className="chart-bar-group">
                  <div 
                    className={`chart-bar-bar ${stat.risk > 1 ? 'high-risk' : ''}`}
                    style={{ height: `${heightPct}%` }}
                  >
                    <div className="chart-bar-tooltip">
                      ₹{stat.amount.toLocaleString('en-IN')} ({stat.risk} Alerts)
                    </div>
                  </div>
                  <span className="chart-bar-label">{stat.month}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Category distribution */}
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h3 className="dashboard-card-title">
              <Award size={18} /> Spending by Category
            </h3>
          </div>
          <div className="category-legend-list">
            {categoryList.map((cat, idx) => (
              <div key={idx} className="legend-item">
                <div className="legend-label-group">
                  <span className="legend-dot" style={{ backgroundColor: cat.color }}></span>
                  <span className="legend-name">{cat.name}</span>
                </div>
                <span className="legend-val">₹{cat.value.toLocaleString('en-IN')}</span>
              </div>
            ))}
            {categoryList.length === 0 && (
              <p style={{ fontSize: '0.85rem', color: '#64748b', textAlign: 'center', marginTop: '30px' }}>
                No active claims recorded.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Lower Row: Recent Alerts & Operations Guide */}
      <div className="dashboard-details-row" style={{ gridTemplateColumns: '1.2fr 1.8fr' }}>
        {/* Fraud alerts */}
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <h3 className="dashboard-card-title" style={{ color: '#b91c1c' }}>
              <AlertTriangle size={18} /> Compliance & Fraud Flags
            </h3>
          </div>
          <div className="system-alerts-list">
            {recentAlerts.map((c) => {
              const isTampered = c.riskLevel === 'High' && c.description.toLowerCase().includes('edit');
              return (
                <div key={c.id} className={`alert-item ${c.riskLevel === 'High' ? 'high' : 'medium'}`}>
                  <div className="alert-icon-box">
                    <AlertTriangle size={16} />
                  </div>
                  <div className="alert-content">
                    <div className="alert-text">
                      {isTampered ? 'Edited Bill Detected' : 'Policy Limit Warning'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#334155', marginTop: '2px' }}>
                      {c.submitter} submitted ₹{c.amount.toLocaleString('en-IN')} for {c.merchant}. {isTampered ? 'Scan shows local text modifications.' : 'Flagged for violating claim rules.'}
                    </div>
                    <div className="alert-meta">
                      <span>ID: {c.id}</span>
                      <span>Risk Score: {(c.anomalyScore * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
            {recentAlerts.length === 0 && (
              <p style={{ fontSize: '0.85rem', color: '#64748b', textAlign: 'center', padding: '20px' }}>
                No warnings detected.
              </p>
            )}
          </div>
        </div>

        {/* Auditor Guidelines (Replaced College Credits) */}
        <div className="dashboard-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="dashboard-card-header">
            <h3 className="dashboard-card-title">
              <HelpCircle size={18} /> Auditor Guidelines & Instructions
            </h3>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.6', flexGrow: 1 }}>
            <p style={{ marginBottom: '10px' }}>
              Use the following process to verify pending claims:
            </p>
            <ul style={{ paddingLeft: '20px', marginBottom: '15px' }}>
              <li><strong>Check Risk Scores:</strong> Focus on claims marked with <strong>High Risk</strong> or <strong>Medium Risk</strong> badges.</li>
              <li><strong>Verify Receipt Edits:</strong> Open the detail modal and toggle <strong>ELA Forensics</strong> to search for glowing highlights which reveal altered numbers.</li>
              <li><strong>Audit Compliance Checks:</strong> Examine the rule validation checklist for limit cap breaches or duplicate receipt serials.</li>
              <li><strong>Approve or Reject:</strong> Confirm the action in the review footer to update the accounts ledger.</li>
            </ul>
            <p style={{ fontSize: '0.8rem', fontStyle: 'italic', color: 'var(--text-light)' }}>
              Tip: You can simulate incoming bills by uploading sample receipts in the <strong>WhatsApp Simulator</strong> tab.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

