import datetime
import json
from enum import Enum
from pathlib import Path

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Status(Enum):
    ACTIVE = 1
    RESOLVED = 2

class Fault():
    def __init__(self, faultID: str, severity: Severity, description: str, timestamp: datetime.datetime, status: Status, sensor_id=None):
        self.faultID = faultID
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.status = status
        self.sensor_id = sensor_id

class FaultDetection():

    def __init__(self):
        self.activeFaults = []
        self.detectionRules = []
    
    # Loads fault detection rules from a JSON file    
    def loadRules(self, file_path: str):
        with open(Path(file_path), "r") as f:
            rules = json.load(f)
        for rule in rules:
            rule["severity"] = Severity[rule["severity"]]
        self.detectionRules = rules

    # Takes sensor data, applies detection rules and returns list of detected faults
    def detectFaults(self, sensorData: dict) -> list:
        detected_faults = []
        for rule in self.detectionRules:
             if rule["sensorId"] == sensorData.get("sensorId"):
                value = sensorData.get("value")
                if self._evaluate_rule(rule["condition"], value, rule["threshold"]):
                    fault = Fault(
                        faultID=rule["faultCode"],
                        severity=rule["severity"],
                        description=rule["message"],
                        timestamp=sensorData.get("timestamp", datetime.datetime.now()),
                        status=Status.ACTIVE,
                        sensor_id=sensorData["sensorId"]
                    )
                    detected_faults.append(fault)
                    self.activeFaults.append(fault)
        return detected_faults
    
    # Returns True if rule condition is met
    def _evaluate_rule(self, condition: str, value: float, threshold: float) -> bool:
        try:
            if condition == ">": return value > threshold
            if condition == "<": return value < threshold
            if condition == ">=": return value >= threshold
            if condition == "<=": return value <= threshold
            if condition in ("==", "="): return value == threshold
            return False
        except TypeError:
            return False

    # Takes a fault and isolates it
    def isolateFault(self, fault: Fault) -> Fault:
        return fault

    # Returns a list of currently active faults
    def getActiveFaults(self) -> list:
        return self.activeFaults