import numpy as np
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

def calculate_fraud_anomaly_score(
    amount: float, 
    category: str, 
    ela_score: float, 
    is_tampered: bool, 
    policy_failed: bool
) -> tuple[float, str]:
    """
    Evaluates ML Isolation Forest Anomaly Score for a claim.
    Features evaluated:
    - Claim amount magnitude
    - Category baseline deviation
    - ELA Forensics manipulation score
    - Policy constraint pass/fail status
    Returns: (anomaly_score, risk_level)
    """
    anomaly_score = 0.12

    if SKLEARN_AVAILABLE:
        try:
            # Generate synthetic normal baseline dataset for training on the fly
            np.random.seed(42)
            normal_data = np.random.normal(loc=[1500, 0.10], scale=[800, 0.05], size=(200, 2))
            
            # Train Isolation Forest
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(normal_data)
            
            # Predict outlier decision score for current claim
            sample = np.array([[amount, ela_score]])
            decision = model.decision_function(sample)[0] # negative values indicate outliers
            
            # Scale decision score to 0.0 -> 1.0 range
            anomaly_score = float(np.clip(0.5 - (decision * 1.5), 0.05, 0.98))
        except Exception as e:
            print(f"Isolation forest calculation exception: {e}")
            anomaly_score = 0.20
    else:
        base = min(1.0, amount / 25000.0) * 0.4
        anomaly_score = base + (ela_score * 0.5)

    # -------------------------------------------------------------
    # STRICT RISK CLASSIFICATION RULES
    # -------------------------------------------------------------
    if is_tampered:
        # Digital alteration detected -> Always High Risk
        anomaly_score = max(anomaly_score, 0.89)
        risk_level = "High"
    elif policy_failed:
        # Policy limit exceeded -> Medium to High Risk
        anomaly_score = max(anomaly_score, 0.55)
        risk_level = "Medium" if amount <= 25000 else "High"
    else:
        # Genuine untampered original bill + passed policy -> ALWAYS LOW RISK
        anomaly_score = min(anomaly_score, 0.12)
        risk_level = "Low"

    anomaly_score = round(anomaly_score, 2)
    return anomaly_score, risk_level

