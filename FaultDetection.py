import datetime
from enum import Enum

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Status(Enum):
    ACTIVE = 1
    RESOLVED = 2

class Fault():
    def __init__(self, faultID: str, severity: Severity, description: str, timestamp: datetime.datetime, status: Status):
        self.faultID = faultID
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.status = status

class FaultDetection():

    def __init__(self):
        self.activeFaults = []
        self.detectionRules = []

    # Takes sensor data, applies detection rules and returns list of detected faults
    def detectFaults(self, sensorData: dict) -> list:
        detected_faults = []
        for rule in self.detectionRules:
            fault = rule(sensorData)
            if fault:
                detected_faults.append(fault)
                self.activeFaults.append(fault) 
        return detected_faults

    # takes a fault and isolates it
    def isolateFault(self, fault: Fault) -> Fault:
        return fault

    # Returns a list of currently active faults
    def getActiveFaults(self) -> list:
        return self.activeFaults