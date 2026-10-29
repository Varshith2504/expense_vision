import React, { useState } from 'react';
import { Search, ShieldAlert, CheckCircle, XCircle, Clock, Eye } from 'lucide-react';

export default function ClaimsTable({ claims, onViewClaim }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [tabFilter, setTabFilter] = useState('All'); 

  // Filter logic
  const filteredClaims = claims.filter(c => {
    const matchesSearch = 
      c.submitter.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.id.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'All' || c.status === statusFilter;
    const matchesRisk = riskFilter === 'All' || c.riskLevel === riskFilter;

    let matchesTab = true;
    if (tabFilter === 'Pending') {
      matchesTab = c.status === 'Pending';
    } else if (tabFilter === 'Reviewed') {
      matchesTab = c.status === 'Approved' || c.status === 'Rejected';
    }

    return matchesSearch && matchesStatus && matchesRisk && matchesTab;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Approved':
        return <span className="badge approved"><CheckCircle size={12} /> Approved</span>;
      case 'Rejected':
        return <span className="badge rejected"><XCircle size={12} /> Rejected</span>;
      default:
        return <span className="badge pending"><Clock size={12} /> Pending</span>;
    }
  };

  const getRiskBadge = (risk) => {
    switch (risk) {
      case 'High':
        return <span className="badge risk-high"><ShieldAlert size={12} /> High ({risk})</span>;
      case 'Medium':
        return <span className="badge risk-medium">Medium ({risk})</span>;
      default:
        return <span className="badge risk-low">Low ({risk})</span>;
    }
  };

  return (
    <div className="claims-table-card">
      {/* Controls Header */}
      <div className="claims-table-controls">
        {/* Search */}
        <div className="search-input-wrapper">
          <Search className="search-icon-svg" size={16} />
          <input 
            type="text" 
            placeholder="Search submitter, merchant, or claim ID..." 
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filters Group */}
        <div className="filter-button-group">
          {/* Tab switches */}
          <div className="table-tabs">
            <button 
              className={`tab-btn ${tabFilter === 'All' ? 'active' : ''}`}
              onClick={() => setTabFilter('All')}
            >
              All Claims ({claims.length})
            </button>
            <button 
              className={`tab-btn ${tabFilter === 'Pending' ? 'active' : ''}`}
              onClick={() => setTabFilter('Pending')}
            >
              Pending ({claims.filter(c => c.status === 'Pending').length})
            </button>
            <button 
              className={`tab-btn ${tabFilter === 'Reviewed' ? 'active' : ''}`}
              onClick={() => setTabFilter('Reviewed')}
            >
              Reviewed ({claims.filter(c => c.status !== 'Pending').length})
            </button>
          </div>

          {/* Risk select */}
          <select 
            className="filter-select"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="All">All Risks</option>
            <option value="High">High Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="Low">Low Risk</option>
          </select>

          {/* Status select */}
          {tabFilter === 'All' && (
            <select 
              className="filter-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Claim ID</th>
              <th>Submitter</th>
              <th>Date</th>
              <th>Merchant</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Risk Assessment</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredClaims.map((claim) => (
              <tr key={claim.id}>
                <td style={{ fontWeight: 600, color: 'var(--primary-blue)' }}>{claim.id}</td>
                <td>
                  <div className="user-cell">
                    <div className="user-avatar">
                      {claim.submitter.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="user-cell-info">
                      <span className="user-cell-name">{claim.submitter}</span>
                      <span className="user-cell-dept">{claim.department}</span>
                    </div>
                  </div>
                </td>
                <td>{claim.date}</td>
                <td style={{ fontWeight: 500 }}>{claim.merchant}</td>
                <td>{claim.category}</td>
                <td style={{ fontWeight: 700 }}>₹{claim.amount.toLocaleString('en-IN')}</td>
                <td>{getRiskBadge(claim.riskLevel)}</td>
                <td>{getStatusBadge(claim.status)}</td>
                <td>
                  <button 
                    className="view-action-btn"
                    onClick={() => onViewClaim(claim)}
                  >
                    <Eye size={12} /> Audit
                  </button>
                </td>
              </tr>
            ))}
            {filteredClaims.length === 0 && (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                  No claims found matching these filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
