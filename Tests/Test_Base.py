import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
from pathlib import Path

class TestBase(unittest.TestCase):
    """Base test class providing common setup and teardown for tests."""
    def setUp(self):
        # Create a temporary directory for test files
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)

    def tearDown(self):
        # Clean up the temporary directory after tests
        self.tmpdir.cleanup()

    def write_csv(self, df, name="test.csv"):
        # Helper method to create a test file in the temporary directory
        path = self.tmp_path / name
        df.to_csv(path, index=False)
        return path