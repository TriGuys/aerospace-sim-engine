from dataclasses import dataclass

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