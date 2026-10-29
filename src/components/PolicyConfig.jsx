import React, { useState } from 'react';
import { ShieldCheck, Save, CheckCircle } from 'lucide-react';

export default function PolicyConfig({ policies, onUpdatePolicies }) {
  const [internLimit, setInternLimit] = useState(policies.internLimit || 3000);
  const [travelCap, setTravelCap] = useState(policies.travelCap || 1500);
  const [itBudget, setItBudget] = useState(policies.itBudget || 50000);
  const [showSavedToast, setShowSavedToast] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    onUpdatePolicies({
      internLimit: parseFloat(internLimit),
      travelCap: parseFloat(travelCap),
      itBudget: parseFloat(itBudget)
    });
    setShowSavedToast(true);
    setTimeout(() => {
      setShowSavedToast(false);
    }, 2000);
  };

  return (
    <div className="dashboard-card" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="dashboard-card-header">
        <h3 className="dashboard-card-title">
          <ShieldCheck size={18} /> Claims & Compliance Policy Settings
        </h3>
        <span className="user-role">Configures audit thresholds</span>
      </div>

      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: '1.5' }}>
        Compliance rules run instantly when a new bill is uploaded. If a claim violates these limits, 
        the system marks the check as <strong>Failed</strong> and sets the warning status accordingly.
      </div>

      <form onSubmit={handleSave}>
        <div className="policy-config-grid">
          {/* Employee Cap */}
          <div className="policy-field-card">
            <div className="policy-field-label">Single Bill Limit Cap (₹)</div>
            <div className="policy-field-input-group">
              <input 
                type="number" 
                value={internLimit}
                onChange={(e) => setInternLimit(e.target.value)}
                className="policy-input"
                min="0"
                required
              />
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-light)', marginTop: '8px' }}>
              Maximum allowable expense amount for a single receipt/bill submission.
            </p>
          </div>

          {/* Travel Cap */}
          <div className="policy-field-card">
            <div className="policy-field-label">Local Cab Travel Cap (₹)</div>
            <div className="policy-field-input-group">
              <input 
                type="number" 
                value={travelCap}
                onChange={(e) => setTravelCap(e.target.value)}
                className="policy-input"
                min="0"
                required
              />
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-light)', marginTop: '8px' }}>
              Maximum reimbursement ceiling for local travel cab fares (e.g., Uber/Ola trips).
            </p>
          </div>

          {/* Department Budget */}
          <div className="policy-field-card">
            <div className="policy-field-label">Monthly Department Budget (₹)</div>
            <div className="policy-field-input-group">
              <input 
                type="number" 
                value={itBudget}
                onChange={(e) => setItBudget(e.target.value)}
                className="policy-input"
                min="0"
                required
              />
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-light)', marginTop: '8px' }}>
              Monthly budget cap allocated for departmental items, office supplies, and team lunches.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifycontent: 'space-between', marginTop: '28px', borderTop: '1px solid var(--border-slate)', paddingTop: '20px' }}>
          <div>
            {showSavedToast && (
              <div className="policy-save-success">
                <CheckCircle size={16} /> Policies successfully saved and updated!
              </div>
            )}
          </div>
          <button type="submit" className="btn btn-approve" style={{ marginLeft: 'auto' }}>
            <Save size={16} /> Save Policy Rules
          </button>
        </div>
      </form>
    </div>
  );
}

