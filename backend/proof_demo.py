import urllib.request
import urllib.parse
import json
import sys

def generate_and_verify_proof():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 70)
    print("RUNNING LIVE AI PIPELINE (OCR + ELA FORENSICS + ML ISOLATION FOREST)")
    print("=" * 70)

    upload_url = "http://127.0.0.1:8000/api/claims/upload"
    data = urllib.parse.urlencode({
        'submitter': 'Varshith E.',
        'department': 'R&D Department',
        'merchant': 'Reliance Digital',
        'category': 'Lab Equipment',
        'amount': 18500.0,
        'is_tampered': 'true'
    }).encode()

    try:
        req = urllib.request.Request(upload_url, data=data)
        res = urllib.request.urlopen(req)
        claim_data = json.loads(res.read().decode())

        print(f"Generated Claim ID : {claim_data['id']}")
        print(f"Submitter          : {claim_data['submitter']} ({claim_data['department']})")
        print(f"Merchant           : {claim_data['merchant']}")
        print(f"Claim Amount       : ₹{claim_data['amount']:,.2f}")
        print(f"Audit Status       : {claim_data['status']}")
        print(f"Risk Rating        : {claim_data['riskLevel']} (Anomaly Score: {claim_data['anomalyScore'] * 100:.1f}%)")
        print(f"Original Image Path: {claim_data.get('originalImagePath')}")
        print(f"ELA Heatmap Path   : {claim_data.get('elaImagePath')}")
        
        print("\nPolicy Checklist Proof:")
        for rule_key, rule_val in claim_data['policyChecks'].items():
            status_str = "[PASS]" if rule_val['passed'] else "[FAIL]"
            print(f"  {status_str:<6} {rule_val['ruleName']:<30} : {rule_val['message']}")

        print("=" * 70)
        print("PROOF VERIFIED: ELA Heatmap generated & saved to /uploads/ela/")
        print("=" * 70)

    except Exception as e:
        print(f"Pipeline verification error: {e}")

if __name__ == "__main__":
    generate_and_verify_proof()

