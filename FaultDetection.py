class Fault():
    def __init__(self, faultID, severity, description, timestamp, status):
        self.faultID = faultID
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.status = status

class FaultDetection():
    def __init__(self):
        pass