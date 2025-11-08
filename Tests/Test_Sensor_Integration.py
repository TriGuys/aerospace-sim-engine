import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
import pandas as pd

from Test_Base import TestBase
from SensorIntegration import SensorIntegration

class TestSensorIntegration(TestBase):

    def setUp(self) -> None:
        super().setUp()
        self.sensor_integration = SensorIntegration()

    def test_get_sensor_data_before_load_raises(self) -> None:
        """(FR3, NFR4) Test that get_sensor_data raises an error before CSV is loaded."""
        with self.assertRaises(ValueError):
            self.sensor_integration.get_sensor_data()

    def test_read_csv_file_not_found_raises(self) -> None:
        """(FR3, NFR3) Test that read_csv raises an error if the file is not found."""
        nonexistent_file = self.tmp_path / "missing.csv"
        with patch("SensorIntegration.logging") as mock_log:
            with self.assertRaises(FileNotFoundError):
                self.sensor_integration.read_csv(nonexistent_file)
            self.assertTrue(mock_log.error.called)

    def test_read_csv_success_sets_data_and_cleans(self) -> None:
        """(FR3) Test that read_csv successfully reads a CSV file and sets the data."""
        raw_data = pd.DataFrame({
            "timestamp": ["00:00:00", "01:00:00", "02:00:00"],
            "sensor_id": ["A1", "A2", " "],  # Third row invalid
            "sensor_type": ["temp", "temp", "temp"],
            "value": ["10", "20", "not_a_number"],  # Last row convert to NaN and drop
            "unit": ["C", "C", "C"],
        })
        csv_path = self.write_csv(raw_data, "sensor_data.csv")

        df = self.sensor_integration.read_csv(csv_path)
        cleaned_data = self.sensor_integration.get_sensor_data()

        # Should drop last bad row
        self.assertEqual(len(df), 2)
        self.assertEqual(len(cleaned_data), 2)
        
        self.assertEqual(cleaned_data.iloc[0]["sensor_id"], "A1")
        self.assertEqual(cleaned_data.iloc[1]["sensor_id"], "A2")

        self.assertTrue(pd.api.types.is_numeric_dtype(cleaned_data["value"]))

    def test_validate_data_missing_columns_raises(self) -> None:
        """(FR3, NFR3) Test that validate_data raises an error if required columns are missing."""
        missing_column_data = pd.DataFrame({
            "timestamp": ["00:00:00"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            # "unit" column is missing
        })
        csv_path = self.write_csv(missing_column_data, "missing_columns.csv")
        with patch("SensorIntegration.logging") as mock_log:
            with self.assertRaises(ValueError):
                self.sensor_integration.read_csv(csv_path)
            self.assertTrue(mock_log.error.called)

    def test_validate_data_unexpected_columns_raises(self) -> None:
        """(FR3, NFR3) Test that validate_data raises an error if unexpected columns are present."""
        extra_column_data = pd.DataFrame({
            "timestamp": ["00:00:00"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            "unit": ["C"],
            "extra_column": ["unexpected"],  # Unexpected column should trigger ValueError
        })
        csv_path = self.write_csv(extra_column_data, "unexpected_columns.csv")
        with patch("SensorIntegration.logging") as mock_log:
            with self.assertRaises(ValueError):
                self.sensor_integration.read_csv(csv_path)
            self.assertTrue(mock_log.error.called)

    def test_timestamp_format_invalid_raises(self) -> None:
        """(FR3, NFR3) Test that invalid timestamp formats raise a ValueError."""
        invalid_timestamp_data = pd.DataFrame({
            "timestamp": ["invalid_time"],
            "sensor_id": ["A1"],
            "sensor_type": ["temp"],
            "value": [10],
            "unit": ["C"],
        })
        csv_path = self.write_csv(invalid_timestamp_data, "invalid_timestamp.csv")
        with patch("SensorIntegration.logging") as mock_log:
            with self.assertRaises(ValueError):
                self.sensor_integration.read_csv(csv_path)
            self.assertTrue(mock_log.error.called)

    def test_rows_missing_required_fields_dropped(self) -> None:
        """(FR3) Test that rows with missing required fields are dropped during cleaning."""
        raw_data = pd.DataFrame({
            "timestamp": ["00:00:00", None, "02:00:00"],
            "sensor_id": ["A1", "A2", None], 
            "sensor_type": ["temp", "temp", "temp"],
            "value": [10, 20, None],
            "unit": ["C", "C", "C"],
        })
        csv_path = self.write_csv(raw_data, "missing_fields.csv")

        df = self.sensor_integration.read_csv(csv_path)
        cleaned_data = self.sensor_integration.get_sensor_data()

        # Should drop rows 2 and 3
        self.assertEqual(len(df), 1)
        self.assertEqual(len(cleaned_data), 1)
        self.assertEqual(cleaned_data.iloc[0]["sensor_id"], "A1")

    def test_module_is_independently_instantiable(self) -> None:
        """(NFR4) Test that SensorIntegration can be instantiated independently."""
        self.assertIsInstance(self.sensor_integration, SensorIntegration)
