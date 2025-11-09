import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
import tkinter as tk

from Test_Base import TestBase
from UserInterface import UserInterface
from Database import AlertDatabase
from AlertModule import AlertModule

class TestUserInterface(TestBase):
    
    def setUp(self) -> None:
        super().setUp()
        # Setup headless Tk root window.
        self.root = tk.Tk()
        self.root.withdraw()  # Prevent window pop-up during tests.

        # Use temporary in-memory database.
        self.db = AlertDatabase(":memory:")
        self.alert_module = AlertModule(self.db)

        # Instantiate UserInterface with mock AlertModule.
        self.ui = UserInterface(self.root, self.alert_module)
        self.ui.all_alerts = [
            (1, "A1", "ENGTEMP", "Critical", "Engine temp exceeded", "13:00:00", "Active", "✅ ❌"),
            (2, "A2", "PRESSURE", "Moderate", "Hydraulic pressure low", "13:10:00", "Active", "✅ ❌"),
            (3, "A3", "CABIN", "Advisory", "Cabin pressure low", "13:15:00", "Active", "✅ ❌"),
        ]

        # Mock GUI table for non-interactive testing.
        self.ui.table = MagicMock()
        self.ui.table.get_children.return_value = [1, 2, 3]
        self.ui.table.item.side_effect = lambda rid, **_: {"values": self.ui.all_alerts[int(rid)-1]} if isinstance(rid, int) else None

    def tearDown(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_display_alerts_populates_table(self) -> None:
        """(FR4) Test that display_alerts populates the GUI alert table."""
        self.ui.display_alerts(self.ui.all_alerts)
        # Verify insert called once per alert.
        self.assertEqual(self.ui.table.insert.call_count, len(self.ui.all_alerts))

    def test_show_critical_alerts_filters_correctly(self) -> None:
        """(FR7, FR4) Test that show_critical_alerts only displays critical alerts."""
        with patch.object(self.ui, "display_alerts") as mock_display:
            self.ui.show_critical_alerts()
            mock_display.assert_called_once()
            filtered = mock_display.call_args[0][0]
            self.assertTrue(all(a[3].lower() == "critical" for a in filtered))

    def test_show_moderate_alerts_filters_correctly(self) -> None:
        """(FR7, FR4) Test moderate alert filtering works."""
        with patch.object(self.ui, "display_alerts") as mock_display:
            self.ui.show_moderate_alerts()
            filtered = mock_display.call_args[0][0]
            self.assertTrue(all(a[3].lower() == "moderate" for a in filtered))

    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_delete_alert_removes_from_table_and_db(self, mock_confirm) -> None:
        """(FR5, NFR1) Test deleting an alert removes it from GUI and DB."""
        # Insert alert into DB
        alert = self.alert_module.create_alert("A1", "TEST", "Critical", "Test fault", "12:00:00")
        row_id = str(alert.alert_id)

        # Mock table.item() to return values tuple
        self.ui.table.item.side_effect = lambda *args, **kwargs: (
            alert.alert_id, "A1", "TEST", "Critical", "Test fault", "12:00:00"
        )

        with patch.object(self.ui.table, "delete") as mock_delete:
            self.ui.delete_alert(row_id)
            mock_delete.assert_called_once_with(row_id)

        # Verify alert was deleted from database
        alerts = self.alert_module.get_all_alerts()
        self.assertFalse(any(a.alert_id == alert.alert_id for a in alerts))