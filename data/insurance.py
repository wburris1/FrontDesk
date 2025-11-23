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
        }
    }
}

PROCEDURES = ["checkup", "vaccination", "xray", "bloodwork", "mental_health"]
INSURANCE_PROVIDERS = ["Aetna", "BlueCross", "Cigna", "UnitedHealthcare", "Medicaid", "Empire Plan"]