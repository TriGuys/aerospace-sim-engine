import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd

from Test_Base import TestBase
from SensorIntegration import SensorIntegration

class TestSensorIntegration(TestBase):

    def setUp(self):
        super().setUp()
        self.si = SensorIntegration()

    def test_get_sensor_data_before_load_raises(self):
        """Test that get_sensor_data raises an error before CSV is loaded."""
        with self.assertRaises(ValueError):
            self.si.get_sensor_data()

    def test_read_csv_file_not_found_raises(self):
        """Test that read_csv raises an error if the file is not found."""
        with self.assertRaises(FileNotFoundError):
            self.si.read_csv(self.tmp_path / "non_existent_file.csv")

    def test_read_csv_success_sets_data_and_cleans(self):
        """Test that read_csv successfully reads a CSV file and sets the data."""
        df = pd.DataFrame({
            "timestamp": ["00:00:00", "01:00:00", "02:00:00"],
            "sensor_id": ["A1", "A2", " "],  # bad row
            "sensor_type": ["temp", "temp", "temp"],
            "value": [10, 20, 30],
            "unit": ["C", "C", "C"],
        })
        path = self.write_csv(df, "ok.csv")
        
        self.si.read_csv(path)
        data = self.si.get_sensor_data()

        # Should drop last bad row
        self.assertEqual(len(data), 2)
        self.assertNotIn(" ", data["sensor_id"].values)

    def test_validate_data_missing_columns_raises(self):
        """Test that validate_data raises an error if required columns are missing."""
        df = pd.DataFrame({
            "timestamp": ["00:00:00"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            # "unit" column is missing
        })
        path = self.write_csv(df, "missing_columns.csv")
        with self.assertRaises(ValueError):
            self.si.read_csv(path)

    def test_validate_data_unexpected_columns_raises(self):
        """Test that validate_data raises an error if unexpected columns are present."""
        df = pd.DataFrame({
            "timestamp": ["00:00:00"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            "unit": ["C"],
            "extra_column": ["unexpected"],  # Unexpected column should trigger ValueError
        })
        path = self.write_csv(df, "unexpected_columns.csv")
        with self.assertRaises(ValueError):
            self.si.read_csv(path)

if __name__ == "__main__":
    unittest.main()