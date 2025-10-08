import datetime

class Fault():
    def __init__(self, faultID: str, severity: enumerate, description: str, timestamp: datetime, status: enumerate):
        self.faultID = faultID
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.status = status

class FaultDetection():
    def __init__(self):
        pass