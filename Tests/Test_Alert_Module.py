import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from Abstractions import AlertCreation, Alert
from Database import AlertDatabase
from AlertModule import AlertModule
from Test_Base import TestBase

class TestAlertModule(TestBase):
    def setUp(self):
        super().setUp()
        self.db_path = self.tmp_path / "alerts.db"
        self.db = AlertDatabase(str(self.db_path))
        self.mod = AlertModule(self.db)

    def tearDown(self):
        try:
            self.db.close()
        finally:
            super().tearDown()

    def test_initial_state_no_alerts(self):
        """Test that the AlertModule starts with no alerts."""
        self.assertEqual(self.mod.get_all_alerts(), [])
        self.assertEqual(self.mod.alerts, [])

    def test_create_alert(self):
        created = self.mod.create_alert(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="high",
            message="Test fault",
            timestamp="12:00:00",
        )

        # Check that the created alert is stored in the module
        self.assertIsInstance(created, Alert)
        self.assertEqual(len(self.mod.alerts), 1)
        self.assertEqual(self.mod.alerts[0].sensor_id, "sensor_1")

        # Check that the alert can be retrieved from the database
        refreshed = self.mod.get_all_alerts()
        self.assertEqual(len(refreshed), 1)
        self.assertEqual(refreshed[0].alert_id, self.mod.alerts[0].alert_id)

    def test_create_alert_invalid_timestamp(self):
        """Test creating an alert with an invalid timestamp fails alert creation."""
        with self.assertRaises(ValueError):
            self.mod.create_alert(
                sensor_id="sensor_invalid",
                fault_code="F999",
                severity="low",
                message="Invalid timestamp test",
                timestamp="2025-01-01",
            )

    def test_get_alert(self):
        """Test retrieving an alert by ID."""
        created = self.db.create(AlertCreation(
            sensor_id="sensor_2",
            fault_code="F002",
            severity="medium",
            message="Another test fault",
            timestamp="00:00:01",
        ))

        # Check that the alert is stored in the module
        alerts = self.mod.get_all_alerts()
        self.assertTrue(any(a.alert_id == created.alert_id for a in alerts))
        self.assertEqual(self.mod.alerts, alerts)

    def test_delete_alert(self):
        """Test deleting an alert by ID."""
        created = self.mod.create_alert(
            sensor_id="sensor_3",
            fault_code="F003",
            severity="low",
            message="Delete test fault",
            timestamp="00:00:02",
        )

        # Delete the alert
        self.assertTrue(self.mod.delete_alert(created.alert_id))
        self.assertFalse(any(a.alert_id == created.alert_id for a in self.mod.alerts))

        # Attempting to delete again should return False
        self.assertFalse(self.mod.delete_alert(created.alert_id))

    def test_delete_nonexistent_alert(self):
        self.assertFalse(self.mod.delete_alert(9999))  # Assuming 9999 does not exist

if __name__ == '__main__':
    unittest.main()