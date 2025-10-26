import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd
from pathlib import Path
import tempfile

from SensorIntegration import SensorIntegration

class TestSensorIntegration(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory for test files."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.si = SensorIntegration()

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tmpdir.cleanup()

    # Helpers
    def _csv_path(self, name: str) -> Path:
        """Get a Path in the temporary directory for a CSV file."""
        return self.tmp_path / name
    
    def _write_df(self, df: pd.DataFrame, path: Path) -> None:
        """Write a DataFrame to CSV at the given path."""
        df.to_csv(path, index=False)

    # Tests
    def test_get_sensor_data_before_load_raises(self):
        """Test that get_sensor_data raises an error before CSV is loaded."""
        with self.assertRaises(ValueError):
            self.si.get_sensor_data()

    def test_read_csv_file_not_found_raises(self):
        """Test that read_csv raises an error if the file is not found."""
        with self.assertRaises(FileNotFoundError):
            self.si.read_csv(self._csv_path("non_existent_file.csv"))

    def test_read_csv_success_sets_data_and_cleans(self):
        """Test that read_csv successfully reads a CSV file and sets the data."""
        df = pd.DataFrame({
            "timestamp": ["2025-01-01T00:00:00Z", "2025-01-01T01:00:00Z", "2025-01-01T02:00:00Z"],
            "sensor_id": ["A1", "A2", " "],  # bad row
            "sensor_type": ["temp", "temp", "temp"],
            "value": [10, 20, 30],
            "unit": ["C", "C", "C"],
        })
        path = self._csv_path("ok.csv")
        self._write_df(df, path)

        self.si.read_csv(path)
        data = self.si.get_sensor_data()

        # Should drop last bad row
        self.assertEqual(len(data), 2)
        self.assertNotIn(" ", data["sensor_id"].values)

if __name__ == "__main__":
    unittest.main()