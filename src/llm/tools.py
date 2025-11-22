from .backend import check_availability, verify_insurance
from data.insurance import PROCEDURES, INSURANCE_PROVIDERS
from data.calendar import DOCTORS

TOOLS = [
    {
        "type": "function",
        "name": "check_availability",
        "description": "Check available appointment slots for a doctor on a given date.",
        "parameters": {
            "type": "object",
            "properties": {
                "day": { "type": "string", "description": "Date, e.g., '11-22-2025'" },
                "time": { "type": "string", "description": "Time, e.g., '2:00 PM'" },
                "doctor": {
                    "type": "string",
                    "enum": DOCTORS,
                    "description": "id of given doctor in this format using doctor's last name: dr_john"
                },
                "appointment_type": { "type": "string", "description": "Type of appointment, e.g., general check-up, annual physical, gynecological exam" },
            },
            "required": ["day", "time", "appointment_type"],
        }
    },
    {
        "name": "verify_insurance",
        "type": "function",
        "description": "Verify whether the clinic accepts the user's insurance.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": { "type": "string", "description": "Full name (first and last)" },
                "provider": {
                    "type": "string",
                    "enum": INSURANCE_PROVIDERS,
                    "description": "Name of insurance provider"
                },
                "procedure": {
                    "type": "string",
                    "enum": PROCEDURES,
                    "description": "Type of procedure: e.g., checkup, mental_health"
                }
            },
            "required": ["name", "provider"],
        }
    }
]


def execute_tool_call(name: str, args: dict):
    """Execute the appropriate backend function based on tool name."""
    if name == "check_availability":
        return check_availability(args["day"], args["time"], args["doctor"], args["appointment_type"])

    if name == "verify_insurance":
        return verify_insurance(args["name"], args["provider"], args["procedure"])

    raise ValueError(f"Unknown tool: {name}")