import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch

from Abstractions import AlertCreation, Alert, Status
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
        """(FR2) Test that the AlertModule starts with no alerts."""
        self.assertEqual(self.alert_module.get_all_alerts(), [])
        self.assertEqual(self.alert_module.alerts, [])

    def test_create_alert(self) -> None:
        """(FR2) Test creating and retrieving an alert."""
        created = self.alert_module.create_alert(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="Critical",
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
        """(FR2, NFR3) Test creating an alert with an invalid timestamp fails alert creation."""
        with patch("AlertModule.logging") as mock_log:
            with self.assertRaises(ValueError):
                self.alert_module.create_alert(
                    sensor_id="sensor_invalid",
                    fault_code="F999",
                    severity="Advisory",
                    message="Invalid timestamp test",
                    timestamp="2025-01-01",
                )
            self.assertTrue(mock_log.error.called)

    def test_get_alert(self) -> None:
        """(FR2) Test retrieving an alert by ID."""
        created = self.database.create(AlertCreation(
            sensor_id="sensor_2",
            fault_code="F002",
            severity="Moderate",
            message="Another test fault",
            timestamp="00:00:01",
        ))

        # Check that the alert is stored in the module
        alerts = self.alert_module.get_all_alerts()
        self.assertTrue(any(a.alert_id == created.alert_id for a in alerts))
        self.assertEqual(self.alert_module.alerts, alerts)

    def test_delete_alert(self) -> None:
        """(FR5) Test deleting an alert by ID."""
        created = self.alert_module.create_alert(
            sensor_id="sensor_3",
            fault_code="F003",
            severity="Advisory",
            message="Delete test fault",
            timestamp="00:00:02",
        )

        # Delete the alert
        self.assertTrue(self.alert_module.delete_alert(created.alert_id))
        self.assertFalse(any(a.alert_id == created.alert_id for a in self.alert_module.alerts))

        # Attempting to delete again should return False
        self.assertFalse(self.alert_module.delete_alert(created.alert_id))

    def test_delete_nonexistent_alert(self) -> None:
        """(FR5) Test deleting a non-existent alert returns False."""
        missing_alert_id = 9999
        self.assertFalse(self.alert_module.delete_alert(missing_alert_id))

    def test_resolve_and_unresolve(self) -> None:
        """(FR4) Test resolving and unresolving an alert."""
        created = self.alert_module.create_alert(
            sensor_id="sensor_4",
            fault_code="F004",
            severity="Critical",
            message="Resolve test fault",
            timestamp="00:00:03",
        )

        # Resolve via module and verify in DB
        self.assertTrue(self.alert_module.resolve_alert(created.alert_id))
        db_after_resolve = self.database.get(created.alert_id)
        self.assertIsNotNone(db_after_resolve)
        assert db_after_resolve is not None
        self.assertEqual(db_after_resolve.status, Status.RESOLVED)

        # Unresolve via module and verify in DB
        self.assertTrue(self.alert_module.unresolve_alert(created.alert_id))
        db_after_unresolve = self.database.get(created.alert_id)
        self.assertIsNotNone(db_after_unresolve)
        assert db_after_unresolve is not None
        self.assertEqual(db_after_unresolve.status, Status.ACTIVE)