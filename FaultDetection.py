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
    """Abstract base class for a fault detection rule.
    
    Defines a standard interface for evaluating sensor values against
    fault thresholds. Subclasses then implement specific comparison logic
    (e.g. GreaterThanRule, LessThanRule, EqualRule).
    
    """

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
        self.active_faults: List[Fault] = []
        self.detection_rules: List[FaultRule] = []
    
    def load_rules(self, file_path: str) -> None:
        """
        Load fault detection rules from a JSON file and create rule objects.

        Each JSON rule is converted into the appropriate FaultRule subclass based on its condition (>, <, =),
        allowing each rule type to evaluate its logic independently through polymorphism.
        """
        with open(Path(file_path), "r") as f:
            rules_data = json.load(f)

        self.detection_rules = []
        for rule in rules_data:
            condition = rule["condition"]
            if condition == ">":
                rule_obj = GreaterThanRule(
                    sensor_id=rule["sensor_id"],
                    threshold=rule["threshold"],
                    fault_code=rule["fault_code"],
                    severity=rule["severity"],
                    message=rule["message"]
                )
            elif condition == "<":
                rule_obj = LessThanRule(
                    sensor_id=rule["sensor_id"],
                    threshold=rule["threshold"],
                    fault_code=rule["fault_code"],
                    severity=rule["severity"],
                    message=rule["message"]
                )
            elif condition in ("=","=="):
                rule_obj = EqualRule(
                    sensor_id=rule["sensor_id"],
                    threshold=rule["threshold"],
                    fault_code=rule["fault_code"],
                    severity=rule["severity"],
                    message=rule["message"]                  
                )
            else: 
                continue

            self.detection_rules.append(rule_obj)

    def detect_faults(self, sensor_data: Dict[str, Any]) -> List[Fault]:
        """
        Apply all loaded FaultRule objects to a single sensor record.

        Each rule evaluates its own condition via its is_triggered() method, demonstrating polymorphism.
        When a rule's condition is satisfied, a corresponding Fault object is created and returned.
        
        Note:
            This method is called internally by detectFromBatch(), 
            which applies detection to an entire pandas DataFrame.

        Args:
            sensor_data (dict): 
                A dictionary representing one sensor data record, expected to include:
                - "timestamp" (str): The time the reading was taken.
                - "sensor_id" (str): The unique identifier of the sensor.
                - "sensor_type" (str): The measurement type (e.g. Temperature, Pressure).
                - "value" (float or int): The numeric reading from the sensor.
                - "unit" (str): The unit of measurement (e.g., "°C", "psi", "V").

        Returns:
            list[Fault]: A list of detected fault objects for the sensor. 
            Returns an empty list if no rules are triggered.
        """

        detected_faults: List[Fault] = []
        for rule in self.detection_rules:
             if rule.sensor_id == sensor_data.get("sensor_id"):
                value = sensor_data.get("value")
                if rule.is_triggered(value):
                    fault = Fault(
                        fault_id=rule.fault_code,
                        sensor_id=sensor_data["sensor_id"],
                        severity=rule.severity,
                        description=rule.message,
                        timestamp = sensor_data["timestamp"],
                        status=Status.ACTIVE
                    )
                    detected_faults.append(fault)
                    self.active_faults.append(fault)
        return detected_faults
    
    def detect_from_batch(self, data_frame: pd.DataFrame) -> List[Fault]:
        """
        Apply fault detection to all rows in a DataFrame.

        Args:
            data_frame (pd.DataFrame): Sensor data with the required columns.

        Returns:
            list[Fault]: A list of all detected faults.
        """
        if not isinstance(data_frame, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame for detectFromBatch()")
        
        all_faults: List[Fault] = []
        for index, row in data_frame.iterrows():
            row_faults = self.detect_faults(row.to_dict())
            all_faults.extend(row_faults)
        return all_faults

    def get_active_faults(self) -> List[Fault]:
        # Return a list of all currently active faults.
        return self.active_faults