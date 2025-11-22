from data.calendar import SLOTS
from data.insurance import INSURANCE_TABLE

def check_availability(day: str, time: str, doctor: str, type: str):
    doctor_info = SLOTS.get(doctor, {})
    available_slots = doctor_info.get("slots", {})
    day_slots = available_slots.get(day, [])

    return {
        "day": day,
        "time": time,
        "doctor": doctor,
        "available": time in day_slots,
        "slots": available_slots,
    }

def verify_insurance(name: str, provider: str, procedure=""):
    provider_data = INSURANCE_TABLE.get(provider, {})
    info = provider_data.get(name.lower(), {})
    policy_number = info.get("policy_number", "")
    provider_accepted = info.get("accepted", False)
    eligibility_active = info.get("eligibility_active", False)
    coverage = info.get("coverage", {})
    procedure_coverage = coverage.get(procedure, "not_covered")

    return {
        "name": name,
        "provider": provider,
        "policy_number": policy_number,
        "eligibility_active": eligibility_active,
        "procedure": procedure,
        "provider_accepted": provider_accepted,
        "procedure_coverage": procedure_coverage
    }