from dataclasses import dataclass

@dataclass(frozen=True)
class Alert:
    alertId: int
    sensorId: str
    faultCode: str
    severity: str
    message: str
    timestamp: str