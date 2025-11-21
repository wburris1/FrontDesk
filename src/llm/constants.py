from enum import Enum, auto

class Intent(Enum):
    APPOINTMENT = auto()
    INSURANCE = auto()
    FAQ = auto()

class AppointmentSlot(Enum):
    PATIENT_NAME = auto()
    DATE = auto()
    TIME = auto()
    REASON = auto()
    DOCTOR = auto()

class InsuranceSlot(Enum):
    PATIENT_NAME = auto()
    PROVIDER = auto()
    POLICY_NUMBER = auto()
    VERIFICATION_TOPIC = auto()