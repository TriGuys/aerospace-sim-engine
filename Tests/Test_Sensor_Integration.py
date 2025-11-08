import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd

from Test_Base import TestBase
from SensorIntegration import SensorIntegration

class TestSensorIntegration(TestBase):

    def setUp(self) -> None:
        super().setUp()
        self.sensor_integration = SensorIntegration()

    def test_get_sensor_data_before_load_raises(self) -> None:
        """Test that get_sensor_data raises an error before CSV is loaded."""
        with self.assertRaises(ValueError):
            self.sensor_integration.get_sensor_data()

    def test_read_csv_file_not_found_raises(self) -> None:
        """Test that read_csv raises an error if the file is not found."""
        nonexistent_file = self.tmp_path / "missing.csv"
        with self.assertRaises(FileNotFoundError):
            self.sensor_integration.read_csv(nonexistent_file)

    def test_read_csv_success_sets_data_and_cleans(self) -> None:
        """Test that read_csv successfully reads a CSV file and sets the data."""
        raw_data = pd.DataFrame({
            "timestamp": ["00:00:00", "01:00:00", "02:00:00"],
            "sensor_id": ["A1", "A2", " "],  # bad row
            "sensor_type": ["temp", "temp", "temp"],
            "value": [10, 20, 30],
            "unit": ["C", "C", "C"],
        })
        csv_path = self.write_csv(raw_data, "sensor_data.csv")

        self.sensor_integration.read_csv(csv_path)
        cleaned_data = self.sensor_integration.get_sensor_data()

        # Should drop last bad row
        self.assertEqual(len(cleaned_data), 2)
        self.assertNotIn(" ", cleaned_data["sensor_id"].values)

    def test_validate_data_missing_columns_raises(self) -> None:
        """Test that validate_data raises an error if required columns are missing."""
        missing_column_data = pd.DataFrame({
            "timestamp": ["00:00:00"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            # "unit" column is missing
        })
        csv_path = self.write_csv(missing_column_data, "missing_columns.csv")
        with self.assertRaises(ValueError):
            self.sensor_integration.read_csv(csv_path)

    def test_validate_data_unexpected_columns_raises(self) -> None:
        """Test that validate_data raises an error if unexpected columns are present."""
        extra_column_data = pd.DataFrame({
            "timestamp": ["00:00:00"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            "unit": ["C"],
            "extra_column": ["unexpected"],  # Unexpected column should trigger ValueError
        })
        csv_path = self.write_csv(extra_column_data, "unexpected_columns.csv")
        with self.assertRaises(ValueError):
            self.sensor_integration.read_csv(csv_path)