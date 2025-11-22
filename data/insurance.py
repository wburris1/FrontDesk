INSURANCE_TABLE = {
    "Aetna": {
        "john doe": {
            "policy_number": "AET-99341278",
            "accepted": True,
            "eligibility_active": True,
            "coverage": {
                "checkup": "covered",
                "vaccination": "covered",
                "xray": "prior_authorization_required",
                "bloodwork": "covered",
                "mental_health": "limited_coverage"
            },
            "what_needs_to_be_verified": [
                "Confirm the patient's plan is active.",
                "Verify if prior authorization is needed for X-rays.",
                "Ask the patient to bring their insurance card and photo ID."
            ]
        }
    },

    "BlueCross": {
        "sarah lee": {
            "policy_number": "BC-55201944",
            "accepted": True,
            "eligibility_active": False,
            "coverage": {
                "checkup": "not_covered",
                "vaccination": "covered",
                "xray": "not_covered",
                "bloodwork": "covered",
                "mental_health": "covered"
            },
            "what_needs_to_be_verified": [
                "Check if the policy has lapsed.",
                "Confirm coverage for routine checkups.",
                "Ask the patient to bring updated insurance documentation."
            ]
        }
    },

    "Cigna": {
        "maria gomez": {
            "policy_number": "CIG-88740022",
            "accepted": False,
            "eligibility_active": True,
            "coverage": {
                "checkup": "covered_out_of_network",
                "vaccination": "covered_out_of_network",
                "xray": "not_covered",
                "bloodwork": "covered_out_of_network",
                "mental_health": "not_covered"
            },
            "what_needs_to_be_verified": [
                "Explain that the clinic does not accept Cigna in-network.",
                "Tell the patient what out-of-network billing means.",
                "Confirm if the patient still wishes to proceed."
            ]
        }
    }
}

PROCEDURES = ["checkup", "vaccination", "xray", "bloodwork", "mental_health"]
INSURANCE_PROVIDERS = ["Aetna", "BlueCross", "Cigna", "UnitedHealthcare", "Medicaid", "Empire Plan"]