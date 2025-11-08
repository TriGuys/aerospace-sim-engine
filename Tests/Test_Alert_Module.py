import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from Abstractions import AlertCreation, Alert
from Database import AlertDatabase
from AlertModule import AlertModule
from Test_Base import TestBase

class TestAlertModule(TestBase):
    def setUp(self) -> None:
        super().setUp()
        db_path = self.tmp_path / "alerts.db"
        self.database = AlertDatabase(str(db_path))
        self.alert_module = AlertModule(self.database)

    def tearDown(self) -> None:
        try:
            self.database.close()
        finally:
            super().tearDown()

    def test_initial_state_no_alerts(self) -> None:
        """Test that the AlertModule starts with no alerts."""
        self.assertEqual(self.alert_module.get_all_alerts(), [])
        self.assertEqual(self.alert_module.alerts, [])

    def test_create_alert(self) -> None:
        created = self.alert_module.create_alert(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="high",
            message="Test fault",
            timestamp="12:00:00",
        )

        # Check that the created alert is stored in the module
        self.assertIsInstance(created, Alert)
        self.assertEqual(len(self.alert_module.alerts), 1)
        self.assertEqual(self.alert_module.alerts[0].sensor_id, "sensor_1")

        # Check that the alert can be retrieved from the database
        refreshed = self.alert_module.get_all_alerts()
        self.assertEqual(len(refreshed), 1)
        self.assertEqual(refreshed[0].alert_id, self.alert_module.alerts[0].alert_id)

    def test_create_alert_invalid_timestamp(self) -> None:
        """Test creating an alert with an invalid timestamp fails alert creation."""
        with self.assertRaises(ValueError):
            self.alert_module.create_alert(
                sensor_id="sensor_invalid",
                fault_code="F999",
                severity="low",
                message="Invalid timestamp test",
                timestamp="2025-01-01",
            )

    def test_get_alert(self) -> None:
        """Test retrieving an alert by ID."""
        created = self.database.create(AlertCreation(
            sensor_id="sensor_2",
            fault_code="F002",
            severity="medium",
            message="Another test fault",
            timestamp="00:00:01",
        ))

        # Check that the alert is stored in the module
        alerts = self.alert_module.get_all_alerts()
        self.assertTrue(any(a.alert_id == created.alert_id for a in alerts))
        self.assertEqual(self.alert_module.alerts, alerts)

    def test_delete_alert(self) -> None:
        """Test deleting an alert by ID."""
        created = self.alert_module.create_alert(
            sensor_id="sensor_3",
            fault_code="F003",
            severity="low",
            message="Delete test fault",
            timestamp="00:00:02",
        )

        # Delete the alert
        self.assertTrue(self.alert_module.delete_alert(created.alert_id))
        self.assertFalse(any(a.alert_id == created.alert_id for a in self.alert_module.alerts))

        # Attempting to delete again should return False
        self.assertFalse(self.alert_module.delete_alert(created.alert_id))

    def test_delete_nonexistent_alert(self) -> None:
        self.assertFalse(self.alert_module.delete_alert(9999))  # Assuming 9999 does not exist