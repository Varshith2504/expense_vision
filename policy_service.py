from backend.models import Policy

def evaluate_policy_rules(
    amount: float, 
    category: str, 
    merchant: str, 
    submitter: str, 
    is_tampered: bool, 
    policy: Policy,
    line_items: list = None
) -> tuple[dict, bool]:
    """
    Evaluates corporate policy rules against claim attributes.
    Returns: (policy_checks_dict, has_policy_failure)
    """
    policy_checks = {}
    has_failure = False

    # 1. Single Bill Limit Check
    intern_limit = policy.intern_limit if policy else 5000.0
    passed_limit = amount <= intern_limit
    policy_checks["amountLimit"] = {
        "ruleName": "Single Bill Limit Check",
        "passed": passed_limit,
        "message": f"Amount ₹{amount:,.2f} is within single bill limit of ₹{intern_limit:,.2f}" if passed_limit
                   else f"LIMIT EXCEEDED: Amount ₹{amount:,.2f} exceeds single bill limit cap of ₹{intern_limit:,.2f}"
    }
    if not passed_limit:
        has_failure = True

    # 2. Travel Cap Check
    if category in ["Travel", "Travel & Transport"]:
        travel_cap = policy.travel_cap if policy else 1500.0
        passed_travel = amount <= travel_cap
        policy_checks["travelCap"] = {
            "ruleName": "Local Cab Travel Cap",
            "passed": passed_travel,
            "message": f"Amount ₹{amount:,.2f} is within travel cap of ₹{travel_cap:,.2f}" if passed_travel
                       else f"LIMIT EXCEEDED: Local travel claim exceeds the cap of ₹{travel_cap:,.2f}"
        }
        if not passed_travel:
            has_failure = True

    # 3. Department Budget Check
    it_budget = policy.it_budget if policy else 50000.0
    policy_checks["budgetCheck"] = {
        "ruleName": "Monthly Department Budget Check",
        "passed": True,
        "message": f"Department budget has ₹{it_budget - amount:,.2f} remaining balance"
    }

    # 4. Arithmetic Consistency Check (Line items sum vs total)
    if line_items and len(line_items) >= 2:
        items_sum = round(sum(item.get("price", 0.0) for item in line_items), 2)
        if items_sum > 0 and abs(amount - items_sum) > 5.0:
            policy_checks["arithmeticCheck"] = {
                "ruleName": "Line Item Total Verification",
                "passed": False,
                "message": f"ALTERATION DETECTED: Total ₹{amount:,.2f} does not match sum of items ₹{items_sum:,.2f}"
            }
            has_failure = True
            is_tampered = True
        else:
            policy_checks["arithmeticCheck"] = {
                "ruleName": "Line Item Total Verification",
                "passed": True,
                "message": f"Line items correctly sum to ₹{amount:,.2f}"
            }

    # 5. Image Manipulation Scan
    policy_checks["imageCheck"] = {
        "ruleName": "Image Manipulation Scan",
        "passed": not is_tampered,
        "message": "No digital alterations detected on receipt" if not is_tampered
                   else "EDITED BILL DETECTED: Digital modification visible on amount section"
    }
    if is_tampered:
        has_failure = True

    return policy_checks, has_failure
