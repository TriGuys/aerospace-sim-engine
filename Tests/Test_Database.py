import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
from pathlib import Path

from Database import AlertDatabase
from Abstractions import AlertCreation

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory for test files."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "alerts.db"
        self.db = AlertDatabase(str(self.db_path))

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tmpdir.cleanup()

    def test_add_and_get_alert(self):
        pass

    def test_get_missing_returns_none(self):
        pass

    def test_delete_alert(self):
        pass

    def test_get_all_descending(self):
        pass

if __name__ == "__main__":
    unittest.main()