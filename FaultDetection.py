import pandas as pd
import json
import logging
from pathlib import Path
from Abstractions import Fault, Severity, Status

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FaultDetection():
    def __init__(self):
        self.activeFaults = []
        self.detectionRules = []
    
    # Loads fault detection rules from a JSON file    
    def loadRules(self, file_path: str):
        with open(Path(file_path), "r") as f:
            rules = json.load(f)
        for rule in rules:
            rule["severity"] = Severity[rule["severity"].upper()]
        self.detectionRules = rules

    def detectFaults(self, sensorData: dict) -> list:
        """
        Applies fault detection rules to a single sensor data record (as a dictionary).

        Note:
            This method is called internally by detectFromBatch(), 
            which applies detection to an entire pandas DataFrame.
        """
        detected_faults = []
        for rule in self.detectionRules:
             if rule["sensorId"] == sensorData.get("sensorId"):
                value = sensorData.get("value")
                if self._evaluate_rule(rule["condition"], value, rule["threshold"]):
                    fault = Fault(
                        fault_id=rule["faultCode"],
                        sensor_id=sensorData["sensorId"],
                        severity=rule["severity"],
                        description=rule["message"],
                        timestamp = sensorData["timestamp"],
                        status=Status.ACTIVE,
                    )
                    detected_faults.append(fault)
                    self.activeFaults.append(fault)
        return detected_faults
    
    # Applies fault detection rules to each row in a pandas DataFrame
    def detectFromBatch(self, dataFrame: pd.DataFrame) -> list:
        if not isinstance(dataFrame, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame for detectFromBatch()")
        
        all_faults = []
        for _, row in dataFrame.iterrows():
            row_faults = self.detectFaults(row.to_dict())
            all_faults.extend(row_faults)
        return all_faults
    
    # Evaluates a fault condition and returns True if rule condition is met
    # Logs any type errors for debugging
    def _evaluate_rule(self, condition: str, value: float, threshold: float) -> bool:
        try:
            if condition == ">": 
                return value > threshold
            if condition == "<": 
                return value < threshold
            if condition == ">=": 
                return value >= threshold
            if condition == "<=": 
                return value <= threshold
            if condition in ("==", "="): 
                return value == threshold
            return False
        except TypeError as e:
            logging.error(
                f"Error evaluating rule: condition={condition}, value={value}, "
                f"threshold={threshold} — {e}"
            )
            return False

    # Returns a list of faults that are active and should be passed to the AlertModule.
    def getActiveFaults(self) -> list:
        return self.activeFaults