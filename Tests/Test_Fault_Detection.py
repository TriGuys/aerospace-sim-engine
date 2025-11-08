import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
from pathlib import Path

import pandas as pd

from FaultDetection import FaultDetection

class TestFaultDetection(unittest.TestCase):
    
    def setUp(self):
        """Set up a temporary directory and FaultDetection instance for testing."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.fd = FaultDetection()
        # Load fault detection rules from a JSON file
        self.fd.load_rules("fault_rules.json")

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tmpdir.cleanup()

    def test_rules_loaded(self):
        """Test that fault detection rules are loaded correctly."""
        self.assertEqual(len(self.fd.detection_rules), 7)

    def test_detect_from_batch_triggers_fault(self):
        """Test that detect_from_batch identifies faults in sensor data."""
        # Create sample sensor data with a known fault
        df = pd.DataFrame([
            {"timestamp": "t1", "sensor_id": "ENG_OILTEMP", "sensorType": "Temperature", "value": 230, "unit": "C"},
            {"timestamp": "t2", "sensor_id": "ENG_OILPRESS", "sensorType": "Pressure", "value": 900, "unit": "kPa"},
            {"timestamp": "t3", "sensor_id": "CABIN_PRESS", "sensorType": "Pressure", "value": 9500, "unit": "ft"},
            {"timestamp": "t4", "sensor_id": "HYDRAULIC_PRESS", "sensorType": "Pressure", "value": -1, "unit": "psi"},
            {"timestamp": "t5", "sensor_id": "FUEL_FLOW", "sensorType": "Flow Rate", "value": 50, "unit": "kg/h"},
            {"timestamp": "t6", "sensor_id": "FUEL_QUANT", "sensorType": "Quantity", "value": 400, "unit": "kg"},
            {"timestamp": "t7", "sensor_id": "ELEC_BUS", "sensorType": "Voltage", "value": 18, "unit": "V"},
        ])

        faults = self.fd.detect_from_batch(df)
        self.assertEqual(len(faults), 7)

        # Verify that active faults are tracked
        self.assertEqual(len(self.fd.get_active_faults()), 7)
    
    def test_detect_from_batch_no_faults(self):
        """Test that detect_from_batch does not identify false positives."""
        normal = {"timestamp": "t_ok", "sensor_id": "ENG_OILTEMP", "sensorType": "Temperature", "value": 200, "unit": "C"}
        before = len(self.fd.get_active_faults())
        new_faults = self.fd.detect_faults(normal)
        after = len(self.fd.get_active_faults())

        self.assertEqual(len(new_faults), 0,)
        self.assertEqual(after, before)

    def test_detect_from_batch_empty_data(self):
        """Test that detect_from_batch handles empty data correctly."""
        with self.assertRaisesRegex(TypeError, r"Expected a pandas DataFrame"):
            self.fd.detect_from_batch({"not": "a dataframe"})

if __name__ == '__main__':
    unittest.main()