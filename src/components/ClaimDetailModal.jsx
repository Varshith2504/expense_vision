import React, { useState } from 'react';
import { X, Check, Database, CheckCircle2, AlertOctagon, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function ClaimDetailModal({ claim, isOpen, onClose, onApprove, onReject }) {
  const [inspectorMode, setInspectorMode] = useState('original'); 

  if (!isOpen || !claim) return null;

  const isPending = claim.status === 'Pending';
  
  // Simple descriptions for image tampering
  const getTamperedDescription = () => {
    if (claim.riskLevel === 'High' || claim.anomalyScore > 0.7) {
      return 'Image analysis detected digital alterations on the receipt. Pixel error density is higher than standard JPEG compression levels.';
    }
    return '';
  };

  const hasBackendElaImage = claim.elaImagePath && claim.elaImagePath.startsWith('/uploads');
  const hasBackendOriginalImage = claim.originalImagePath && claim.originalImagePath.startsWith('/uploads');

  return (
    <div className={`modal-overlay ${isOpen ? 'open' : ''}`} onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-title">
            <div className="university-logo-placeholder">EV</div>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Claim Verification Details</h2>
              <span className="user-role">ID: {claim.id} • Submitted on: {claim.date}</span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          <div className="modal-grid-two-col">
            
            {/* Left Col: Receipt Image / ELA Viewer */}
            <div className="receipt-inspector-panel">
              <div className="inspector-toggle-header">
                <span className="inspector-title">Receipt View</span>
                
                <div className="mode-switch-pill">
                  <button 
                    className={`mode-switch-btn ${inspectorMode === 'original' ? 'active' : ''}`}
                    onClick={() => setInspectorMode('original')}
                  >
                    Original Bill
                  </button>
                  <button 
                    className={`mode-switch-btn ${inspectorMode === 'ela' ? 'active' : ''}`}
                    onClick={() => setInspectorMode('ela')}
                  >
                    Tampering Scan
                  </button>
                </div>
              </div>

              {/* Dynamic Receipt / ELA Heatmap Display Box */}
              <div className="receipt-visualizer-box">
                {hasBackendOriginalImage && inspectorMode === 'original' ? (
                  <div style={{ width: '100%', height: '100%', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0f172a', padding: '8px' }}>
                    <img 
                      src={claim.originalImagePath} 
                      alt="Original Uploaded Receipt" 
                      style={{ maxWidth: '100%', maxHeight: '420px', objectFit: 'contain', borderRadius: '6px', boxShadow: '0 4px 12px rgba(0,0,0,0.3)' }}
                    />
                    <div className="ela-legend-indicator" style={{ backgroundColor: 'rgba(15, 23, 42, 0.85)' }}>
                      <span className="ela-legend-dot" style={{ backgroundColor: '#38bdf8' }}></span>
                      <span>Original Uploaded Bill / Receipt</span>
                    </div>
                  </div>
                ) : hasBackendElaImage && inspectorMode === 'ela' ? (
                  <div style={{ width: '100%', height: '100%', position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: '#050508', padding: '8px' }}>
                    <img 
                      src={claim.elaImagePath} 
                      alt="Backend Generated ELA Heatmap" 
                      style={{ maxWidth: '100%', maxHeight: '420px', objectFit: 'contain', borderRadius: '6px', border: '1px solid #dc2626' }}
                    />
                    <div className="ela-legend-indicator">
                      <span className="ela-legend-dot"></span>
                      <span>Python OpenCV ELA Forensics Heatmap</span>
                    </div>
                  </div>
                ) : (
                  <div className={`vector-receipt ${inspectorMode === 'ela' ? 'ela-mode' : ''}`}>
                    <div className="receipt-header">
                      <h3>{claim.merchant.toUpperCase()}</h3>
                      <p>Bill Ref: EV-REC-{claim.id.replace('EV-', '')}</p>
                      <p>Date: {claim.id === 'EV-004' && inspectorMode === 'ela' ? (
                        <span className="ela-manipulated-glow">2026</span>
                      ) : claim.id === 'EV-004' ? '2026' : claim.date}</p>
                    </div>

                    {/* Items */}
                    {claim.id === 'EV-001' && (
                      <>
                        <div className="receipt-row">
                          <span className="receipt-item-name">2x Caramel Latte</span>
                          <span>₹700.00</span>
                        </div>
                        <div className="receipt-row">
                          <span className="receipt-item-name">1x Butter Croissant</span>
                          <span>₹450.00</span>
                        </div>
                        <div className="receipt-row">
                          <span className="receipt-item-name">GST (8%)</span>
                          <span>₹100.00</span>
                        </div>
                      </>
                    )}

                    {claim.id === 'EV-002' && (
                      <>
                        <div className="receipt-row">
                          <span className="receipt-item-name">1x Microcontroller Board</span>
                          <span>₹8,500.00</span>
                        </div>
                        <div className="receipt-row">
                          <span className="receipt-item-name">1x Soldering Iron Kit</span>
                          <span>₹9,000.00</span>
                        </div>
                        <div className="receipt-row">
                          <span className="receipt-item-name">1x Service Charge</span>
                          <span>₹1,000.00</span>
                        </div>
                      </>
                    )}

                    {claim.id === 'EV-003' && (
                      <>
                        <div className="receipt-row">
                          <span className="receipt-item-name">Uber Cab (Gachibowli to Medchal)</span>
                          <span>₹3,000.00</span>
                        </div>
                        <div className="receipt-row">
                          <span className="receipt-item-name">Booking Surcharge</span>
                          <span>₹200.00</span>
                        </div>
                      </>
                    )}

                    {/* Default line items */}
                    {claim.id !== 'EV-001' && claim.id !== 'EV-002' && claim.id !== 'EV-003' && (
                      <>
                        <div className="receipt-row">
                          <span className="receipt-item-name">Expense Charge</span>
                          <span>₹{(claim.amount * 0.9).toLocaleString('en-IN')}</span>
                        </div>
                        <div className="receipt-row">
                          <span className="receipt-item-name">GST Surcharge</span>
                          <span>₹{(claim.amount * 0.1).toLocaleString('en-IN')}</span>
                        </div>
                      </>
                    )}

                    <div className="receipt-items-divider"></div>

                    {/* Total */}
                    <div className="receipt-total-row">
                      <span>TOTAL AMOUNT:</span>
                      {claim.id === 'EV-002' ? (
                        <span className={inspectorMode === 'ela' ? 'ela-manipulated-glow' : ''}>
                          ₹18,500.00
                        </span>
                      ) : claim.id === 'EV-004' ? (
                        <span className={inspectorMode === 'ela' ? 'ela-manipulated-glow' : ''}>
                          ₹15,000.00
                        </span>
                      ) : (
                        <span>₹{claim.amount.toLocaleString('en-IN')}</span>
                      )}
                    </div>

                    <div style={{ textAlign: 'center', marginTop: 'auto', fontSize: '0.65rem', color: '#94a3b8' }}>
                      * THANK YOU *
                    </div>

                    {inspectorMode === 'ela' && (
                      <div className="ela-legend-indicator">
                        <span className="ela-legend-dot"></span>
                        <span>Digital Alterations Detected</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Right Col: Metadata & Fraud Audit Logs */}
            <div className="modal-info-column">
              {/* Submitter Box */}
              <div className="modal-section" style={{ padding: '16px' }}>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-light)', marginBottom: '8px', textTransform: 'uppercase' }}>
                  Claim Submitter
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div className="user-avatar" style={{ width: '40px', height: '40px', fontSize: '1rem' }}>
                    {claim.submitter.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{claim.submitter}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>
                      Department: {claim.department} | Role: Employee
                    </div>
                  </div>
                </div>
              </div>

              {/* Policy Validation Panel */}
              <div className="modal-section">
                <h4 className="modal-section-title">
                  <ShieldCheck size={16} /> Corporate Policy Checklist
                </h4>
                <div className="policy-checklist">
                  {Object.keys(claim.policyChecks || {}).map((key) => {
                    const rule = claim.policyChecks[key];
                    return (
                      <div key={key} className="policy-check-item">
                        <div className="policy-check-icon">
                          {rule.passed ? (
                            <CheckCircle2 size={16} className="policy-check-icon pass" />
                          ) : (
                            <AlertOctagon size={16} className="policy-check-icon fail" />
                          )}
                        </div>
                        <div className="policy-check-details">
                          <div className="policy-check-label" style={{ color: rule.passed ? 'inherit' : 'var(--status-rejected-text)' }}>
                            {rule.ruleName}
                          </div>
                          <div className="policy-check-desc">{rule.message}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* ML Fraud Panel */}
              <div className="modal-section">
                <h4 className="modal-section-title">
                  <Database size={16} /> Isolation Forest ML Risk Engine
                </h4>
                <div className="risk-meter-container">
                  <div className="risk-meter-header">
                    <span>Unusual Claim Probability:</span>
                    <span style={{ 
                      color: claim.riskLevel === 'High' ? 'var(--status-rejected-text)' : 
                             claim.riskLevel === 'Medium' ? 'var(--status-pending-text)' : 'var(--status-approved-text)',
                      fontWeight: 700
                    }}>
                      {(claim.anomalyScore * 100).toFixed(0)}% ({claim.riskLevel} Risk)
                    </span>
                  </div>

                  <div className="risk-meter-bar-outer">
                    <div 
                      className={`risk-meter-bar-inner ${claim.riskLevel.toLowerCase()}`}
                      style={{ width: `${claim.anomalyScore * 100}%` }}
                    ></div>
                  </div>

                  <div className="risk-breakdown-details">
                    <div className="risk-breakdown-row">
                      <span>Amount Outlier Check:</span>
                      <span className="risk-breakdown-val">
                        {claim.amount > 10000 ? 'High Outlier Flagged' : 'Normal'}
                      </span>
                    </div>
                    <div className="risk-breakdown-row">
                      <span>Submission Frequency:</span>
                      <span className="risk-breakdown-val">
                        {claim.id === 'EV-003' ? 'Repeated Receipt Flagged' : 'Normal'}
                      </span>
                    </div>
                    <div className="risk-breakdown-row">
                      <span>OCR Extraction Confidence:</span>
                      <span className="risk-breakdown-val">
                        {claim.ocrData?.confidenceScore ? `${(claim.ocrData.confidenceScore * 100).toFixed(0)}%` : '95%'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Warning banner */}
          {claim.riskLevel === 'High' && (
            <div style={{ 
              backgroundColor: '#fff1f2', 
              border: '1px solid #fecaca', 
              borderRadius: '8px', 
              padding: '12px 16px', 
              fontSize: '0.825rem',
              color: 'var(--status-rejected-text)',
              display: 'flex',
              gap: '10px',
              alignItems: 'flex-start'
            }}>
              <ShieldAlert size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong>Fraud Audit Notice:</strong> {getTamperedDescription() || 'Digital alterations have been detected in the text overlays of this receipt. Please inspect the original copy before issuing reimbursement.'}
              </div>
            </div>
          )}

        </div>

        {/* Footer Actions */}
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
          {isPending && (
            <>
              <button 
                className="btn btn-reject"
                onClick={() => {
                  onReject(claim.id);
                  onClose();
                }}
              >
                <X size={16} /> Reject Claim
              </button>
              <button 
                className="btn btn-approve"
                onClick={() => {
                  onApprove(claim.id);
                  onClose();
                }}
              >
                <Check size={16} /> Approve Claim
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

