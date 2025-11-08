import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from Database import AlertDatabase
from Abstractions import AlertCreation
from Test_Base import TestBase

class TestDatabase(TestBase):

    def setUp(self) -> None:
        super().setUp()
        db_path = self.tmp_path / "alerts.db"
        self.database = AlertDatabase(str(db_path))

    def tearDown(self) -> None:
        try:
            self.database.close()
        finally:
            super().tearDown()

    def test_add_and_get_alert(self) -> None:
        """Test adding an alert and retrieving it."""
        creation = AlertCreation(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="high",
            message="Test fault",
            timestamp="00:00:00",
        )
        created = self.database.create(creation)
        retrieved = self.database.get(created.alert_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.sensor_id, creation.sensor_id)
        self.assertEqual(retrieved.fault_code, creation.fault_code)
        self.assertEqual(retrieved.severity, creation.severity)
        self.assertEqual(retrieved.message, creation.message)
        self.assertEqual(retrieved.timestamp, creation.timestamp)

    def test_create_rejects_invalid_timestamp(self) -> None:
        """Test that creating an alert with an invalid timestamp raises ValueError."""
        bad_creation = AlertCreation(
            sensor_id="sensor_invalid",
            fault_code="F999",
            severity="low",
            message="Invalid timestamp test",
            timestamp="25:61:99",
        )
        with self.assertRaises(ValueError):
            self.database.create(bad_creation)

    def test_get_missing_returns_none(self) -> None:
        """Test retrieving creation non-existent alert."""
        self.assertIsNone(self.database.get(9999))  # Assuming 9999 does not exist

    def test_delete_alert(self) -> None:
        """Test deleting an alert."""
        creation = AlertCreation(
            sensor_id="sensor_1",
            fault_code="F001",
            severity="high",
            message="Test fault",
            timestamp="00:00:00",
        )
        created = self.database.create(creation)

        self.assertTrue(self.database.delete(created.alert_id))
        self.assertIsNone(self.database.get(created.alert_id))
        self.assertFalse(self.database.delete(created.alert_id))  # Already deleted

    def test_get_all_descending(self) -> None:
        """Test retrieving all alerts in descending order."""
        created_ids = []
        for i in range(3):
            creation = AlertCreation(
                sensor_id=f"sensor_{i}",
                fault_code=f"F00{i}",
                severity="medium",
                message=f"Test fault {i}",
                timestamp=f"00:00:0{i}",
            )
            created = self.database.create(creation)
            created_ids.append(created.alert_id)

        all_alerts = self.database.get_all()
        self.assertEqual([a.alert_id for a in all_alerts], created_ids)