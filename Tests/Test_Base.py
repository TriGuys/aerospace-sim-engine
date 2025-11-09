import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
from pathlib import Path

import pandas as pd

class TestBase(unittest.TestCase):
    """Base test class providing common setup and teardown for tests."""
    
    def setUp(self) -> None:
        """Set up a temporary directory for tests."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

    def tearDown(self) -> None:
        """Clean up the temporary directory after tests."""
        self.tmpdir.cleanup()

    def write_csv(self, df: pd.DataFrame, name: str = "test.csv") -> Path:
        """Write a DataFrame to a CSV file in the temporary directory."""
        csv_path = self.tmp_path / name
        df.to_csv(csv_path, index=False)
        return csv_path