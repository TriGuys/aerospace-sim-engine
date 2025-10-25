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

    def test_get_sensor_data_before_load_raises(self):
        pass

    def test_read_csv_file_not_found_raises(self):
        pass

    def test_read_csv_success_sets_data_and_cleans(self):
        pass

if __name__ == "__main__":
    unittest.main()