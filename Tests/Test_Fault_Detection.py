import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd

from FaultDetection import FaultDetection
from Test_Base import TestBase

class TestFaultDetection(TestBase):
    
    def setUp(self) -> None:
        super().setUp()
        self.fault_detection = FaultDetection()
        # Load fault detection rules from a JSON file
        self.fault_detection.load_rules("fault_rules.json")

    def test_rules_loaded_with_valid_structure(self) -> None:
        """(FR1) Test that fault detection rules are loaded correctly."""
        rules = self.fault_detection.detection_rules

        # Check rules exist
        self.assertGreater(len(rules), 0, "No fault detection rules loaded from JSON file.")

        # Check each rule has required keys
        required_keys = {"sensor_id", "fault_code", "condition", "threshold", "parameter", "severity", "message"}
        for rule in rules:
            self.assertTrue(
                required_keys.issubset(rule.keys()),
                f"Rule is missing required fields: {rule}"
            )

    def test_detect_from_batch_triggers_fault(self) -> None:
        """(FR1) Test that detect_from_batch identifies faults in sensor data."""
        # Create sample sensor data with a known fault
        df = pd.DataFrame([
            {"timestamp": "00:00:01", "sensor_id": "ENG_OILTEMP", "sensor_type": "Temperature", "value": 230, "unit": "C"},
            {"timestamp": "00:00:02", "sensor_id": "ENG_OILPRESS", "sensor_type": "Pressure", "value": 900, "unit": "kPa"},
            {"timestamp": "00:00:03", "sensor_id": "CABIN_PRESS", "sensor_type": "Pressure", "value": 9500, "unit": "ft"},
            {"timestamp": "00:00:04", "sensor_id": "HYDRAULIC_PRESS", "sensor_type": "Pressure", "value": -1, "unit": "psi"},
            {"timestamp": "00:00:05", "sensor_id": "FUEL_FLOW", "sensor_type": "Flow Rate", "value": 50, "unit": "kg/h"},
            {"timestamp": "00:00:06", "sensor_id": "FUEL_QUANT", "sensor_type": "Quantity", "value": 400, "unit": "kg"},
            {"timestamp": "00:00:07", "sensor_id": "ELEC_BUS", "sensor_type": "Voltage", "value": 18, "unit": "V"},
        ])

        detected_faults = self.fault_detection.detect_from_batch(df)
        self.assertEqual(len(detected_faults), 7)

        # Verify that active faults are tracked
        self.assertEqual(len(self.fault_detection.get_active_faults()), 7)
    
    def test_detect_from_batch_no_faults(self) -> None:
        """(FR1) Test that detect_from_batch does not identify false positives."""
        normal_sensor_data = {"timestamp": "00:00:02", "sensor_id": "ENG_OILTEMP", "sensor_type": "Temperature", "value": 200, "unit": "C"}
        before = len(self.fault_detection.get_active_faults())
        new_faults = self.fault_detection.detect_faults(normal_sensor_data)
        after = len(self.fault_detection.get_active_faults())

        self.assertEqual(len(new_faults), 0)
        self.assertEqual(after, before)

    def test_detect_from_batch_empty_data(self) -> None:
        """(FR1) Test that detect_from_batch handles empty data correctly."""
        with self.assertRaisesRegex(TypeError, r"Expected a pandas DataFrame"):
            self.fault_detection.detect_from_batch({"not": "a dataframe"})

    def test_load_rules_invalid_file_raises(self) -> None:
        """(NFR4) Test that loading rules from an invalid file raises FileNotFoundError."""
        fault_detection_new = FaultDetection()
        with self.assertRaises(FileNotFoundError):
            fault_detection_new.load_rules("invalid_rules.json")