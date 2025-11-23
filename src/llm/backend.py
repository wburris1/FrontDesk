from data.calendar import SLOTS
from data.insurance import INSURANCE_TABLE

def check_availability(day: str, time: str, reason: str, doctor: str = ""):
    # If a specific doctor is requested
    if doctor:
        doctor_info = SLOTS.get(doctor, {})
        available_slots = doctor_info.get("slots", {})
        day_slots = available_slots.get(day, [])
        
        return {
            "day": day,
            "time": time,
            "reason": reason,
            "doctor": doctor,
            "available": time in day_slots,
            "slots": available_slots,
        }

    # If no doctor specified, check all doctors
    available_doctors = []
    all_slots = {}

    for doc_name, doc_info in SLOTS.items():
        doctor_slots = doc_info.get("slots", {})
        day_slots = doctor_slots.get(day, [])
        all_slots[doc_name] = doctor_slots
        if time in day_slots:
            available_doctors.append(doc_name)

    return {
        "day": day,
        "time": time,
        "reason": reason,
        "doctor": None if not available_doctors else available_doctors,
        "available": bool(available_doctors),
        "slots": all_slots,
    }

def verify_insurance(name: str, provider: str, procedure: str = ""):
    provider_data = INSURANCE_TABLE.get(provider, {})
    info = provider_data.get(name.lower(), {})
    #policy_number = info.get("policy_number", "")
    provider_accepted = info.get("accepted", False)
    eligibility_active = info.get("eligibility_active", False)
    coverage = info.get("coverage", {})
    procedure_coverage = coverage.get(procedure, "not_covered")

    return {
        "name": name,
        "provider": provider,
        #"policy_number": policy_number,
        "eligibility_active": eligibility_active,
        "procedure": procedure,
        "provider_accepted": provider_accepted,
        "procedure_coverage": procedure_coverage
    }