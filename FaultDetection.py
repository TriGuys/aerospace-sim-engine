<<<<<<< HEAD
import pandas as pd
import json
import logging
from pathlib import Path
from Abstractions import Fault, Severity, Status

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
=======
import datetime
from enum import Enum

class Fault():
    def __init__(self, faultID: str, severity: Enum, description: str, timestamp: datetime.datetime, status: Enum):
        self.faultID = faultID
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.status = status
>>>>>>> 0aa9189 (correct type hints for fault class and getActiveFaults function)

class FaultDetection():
    def __init__(self):
        self.activeFaults = []
        self.detectionRules = []
    
    # Loads fault detection rules from a JSON file    
    def loadRules(self, file_path: str):
        with open(Path(file_path), "r") as f:
            rules = json.load(f)
        for rule in rules:
            rule["severity"] = Severity[rule["severity"].capitalize()]
        self.detectionRules = rules

    def detectFaults(self, sensorData: dict) -> list:
        """
        Applies fault detection rules to a single sensor data record (as a dictionary).

        This method evaluates sensor data against all of the fault detection rules. 
        If a rule condition is met, a corresponding `Fault` object is created and added to the list of detected faults.

        Note:
            This method is called internally by detectFromBatch(), 
            which applies detection to an entire pandas DataFrame.

        Args:
            sensorData (dict): 
                A dictionary representing one sensor data record, expected to include:
                - "timestamp" (str): The time the reading was taken.
                - "sensor_id" (str): The unique identifier of the sensor.
                - "sensorType" (str): The category or measurement type (e.g. Temperature, Pressure).
                - "value" (float or int): The numeric reading from the sensor.
                - "unit" (str): The unit of measurement for the sensor value (e.g., "°C", "psi", "V").

        Returns:
            list[Fault]: 
                A list of Fault objects representing all of the faults detected
                for this specific sensor record. Returns an empty list if
                none of the fault rules were triggered.
        """

        detected_faults = []
        for rule in self.detectionRules:
             if rule["sensor_id"] == sensorData.get("sensor_id"):
                value = sensorData.get("value")
                if self._evaluate_rule(rule["condition"], value, rule["threshold"]):
                    fault = Fault(
                        fault_id=rule["faultCode"],
                        sensor_id=sensorData["sensor_id"],
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
        for index, row in dataFrame.iterrows():
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

<<<<<<< HEAD
    # Returns a list of faults that are active and should be passed to the AlertModule.
=======
    # takes a fault and isolates it
    def isolateFault(self, fault: Fault) -> Fault:
        return fault

    # Returns a list of currently active faults
>>>>>>> 0aa9189 (correct type hints for fault class and getActiveFaults function)
    def getActiveFaults(self) -> list:
        return self.activeFaults