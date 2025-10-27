import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
from pathlib import Path

from Abstractions import AlertCreation, Alert
from Database import AlertDatabase
from AlertModule import AlertModule

class TestAlertModule(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory for test files."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.db_path = self.tmp_path / "alerts.db"
        self.db = AlertDatabase(str(self.db_path))
        self.am = AlertModule(self.db)

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tmpdir.cleanup()