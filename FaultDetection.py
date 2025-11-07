import pandas as pd
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from abc import ABC, abstractmethod
from Abstractions import Fault, Severity, Status

# Configure logging for the module.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FaultRule(ABC):
    """Abstract base class for a fault detection rule."""

    def __init__(self, sensor_id: str, threshold: float, fault_code: str, severity: str, message: str):
        self.sensor_id = sensor_id
        self.threshold = threshold
        self.fault_code = fault_code
        self.severity = Severity[severity.capitalize()]
        self.message = message

    @abstractmethod
    def is_triggered(self, value: float) -> bool:
        """Evaluate whether the rule condition is met."""
        pass

class GreaterThanRule(FaultRule):
    """Rule triggered when value exceeds the threshold."""
    def is_triggered(self, value: float) -> bool:
        return value > self.threshold


class LessThanRule(FaultRule):
    """Rule triggered when value falls below the threshold."""
    def is_triggered(self, value: float) -> bool:
        return value < self.threshold

class EqualRule(FaultRule):
    """Rule triggered when value equals the threshold."""
    def is_triggered(self, value: float) -> bool:
        return value == self.threshold
    
class FaultDetection():
    """Detects faults from sensor data using configurable fault rules sets."""
    def __init__(self) -> None:
        self.activeFaults: List[Fault] = []
        self.detectionRules: List[Dict[str, Any]] = []
    
    def loadRules(self, file_path: str) -> None:
        """
        Load fault detection rules from a JSON file and instantiate rule objects.

        Args:
            file_path(str): Path to the JSON file containing the fault detection rules. 
        """
        with open(Path(file_path), "r") as f:
            rules_data = json.load(f)

        self.detectionRules = []
        for rule in rules_data:
            condition = rule["condition"]
            if condition == ">":
                rule_obj = GreaterThanRule(
                    sensor_id=rule["sensor_id"],
                    threshold=rule["threshold"],
                    fault_code=rule["faultCode"],
                    severity=rule["severity"],
                    message=rule["message"]
                )
            elif condition == "<":
                rule_obj = LessThanRule(
                    sensor_id=rule["sensor_id"],
                    threshold=rule["threshold"],
                    fault_code=rule["faultCode"],
                    severity=rule["severity"],
                    message=rule["message"]
                )
            elif condition in ("=","=="):
                rule_obj = EqualRule(
                    sensor_id=rule["sensor_id"],
                    threshold=rule["threshold"],
                    fault_code=rule["faultCode"],
                    severity=rule["severity"],
                    message=rule["message"]                  
                )
            else: 
                continue

            self.detectionRules.append(rule_obj)

    def detectFaults(self, sensorData: Dict[str, Any]) -> List[Fault]:
        """
        Apply fault detection rules to a single sensor record.

        Note:
            This method is called internally by detectFromBatch(), 
            which applies detection to an entire pandas DataFrame.

        Args:
            sensorData (dict): 
                A dictionary representing one sensor data record, expected to include:
                - "timestamp" (str): The time the reading was taken.
                - "sensor_id" (str): The unique identifier of the sensor.
                - "sensor_type" (str): The category or measurement type (e.g. Temperature, Pressure).
                - "value" (float or int): The numeric reading from the sensor.
                - "unit" (str): The unit of measurement for the sensor value (e.g., "°C", "psi", "V").

        Returns:
            list[Fault]: List of detected fault objects for the sensor. 
            Returns an empty list if none of the fault rules were triggered.
        """

        detected_faults: List[Fault] = []
        for rule in self.detectionRules:
             if rule.sensor_id == sensorData.get("sensor_id"):
                value = sensorData.get("value")
                if rule.is_triggered(value):
                    fault = Fault(
                        fault_id=rule.fault_code,
                        sensor_id=sensorData["sensor_id"],
                        severity=rule.severity,
                        description=rule.message,
                        timestamp = sensorData["timestamp"],
                        status=Status.ACTIVE
                    )
                    detected_faults.append(fault)
                    self.activeFaults.append(fault)
        return detected_faults
    
    def detectFromBatch(self, dataFrame: pd.DataFrame) -> List[Fault]:
        """
        Apply fault detection to all rows in a DataFrame.

        Args:
            dataFrame (pd.DataFrame): Sensor data with the required columns.

        Returns:
            list[Fault]: A list of all detected faults.
        """
        if not isinstance(dataFrame, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame for detectFromBatch()")
        
        all_faults: List[Fault] = []
        for index, row in dataFrame.iterrows():
            row_faults = self.detectFaults(row.to_dict())
            all_faults.extend(row_faults)
        return all_faults

    def getActiveFaults(self) -> List[Fault]:
        # Return a list of all currently active faults.
        return self.activeFaults