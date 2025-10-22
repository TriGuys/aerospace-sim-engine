from enum import Enum
from dataclasses import dataclass

class Severity(Enum):
    Advisory = 1
    Moderate = 2
    Critical = 3

class Status(Enum):
    ACTIVE = 1
    RESOLVED = 2

@dataclass(frozen=True)
class Fault:
    fault_id: str
    sensor_id: str
    severity: Severity
    description: str
    timestamp: str
    status: Status

@dataclass(frozen=True)
class AlertCreation:
    sensor_id: str
    fault_code: str
    severity: str
    message: str
    timestamp: str

@dataclass(frozen=True)
class Alert:
    alert_id: int
    sensor_id: str
    fault_code: str
    severity: str
    message: str
    timestamp: str