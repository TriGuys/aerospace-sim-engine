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
        """Test adding an alert and retrieving it."""
        a = AlertCreation(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="high",
            message="Test fault",
            timestamp="2025-01-01T00:00:00Z",
        )
        alert_id = self.db.create(a)
        retrieved = self.db.get(alert_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.sensor_id, a.sensor_id)
        self.assertEqual(retrieved.fault_code, a.fault_code)
        self.assertEqual(retrieved.severity, a.severity)
        self.assertEqual(retrieved.message, a.message)
        self.assertEqual(retrieved.timestamp, a.timestamp)

    def test_get_missing_returns_none(self):
        """Test retrieving a non-existent alert."""
        self.assertIsNone(self.db.get(9999))  # Assuming 9999 does not exist

    def test_delete_alert(self):
        """Test deleting an alert."""
        a = AlertCreation(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="high",
            message="Test fault",
            timestamp="2025-01-01T00:00:00Z",
        )
        alert_id = self.db.create(a)

        self.assertTrue(self.db.delete(alert_id))
        self.assertIsNone(self.db.get(alert_id))
        self.assertFalse(self.db.delete(alert_id))  # Already deleted

    def test_get_all_descending(self):
        """Test retrieving all alerts in descending order."""
        ids = []
        for i in range(3):
            a = AlertCreation(
                sensor_id=f"sensor_{i}",
                fault_code=f"F00{i}",
                severity="medium",
                message=f"Test fault {i}",
                timestamp=f"2025-01-01T00:00:0{i}Z",
            )
            ids.append(self.db.create(a))

        all_alerts = self.db.get_all()
        self.assertEqual([al.alert_id for al in all_alerts], sorted(ids, reverse=True))

if __name__ == "__main__":
    unittest.main()