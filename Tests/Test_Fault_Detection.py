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

    def tearDown(self):
        """Clean up the temporary directory."""
        self.tmpdir.cleanup()