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
        # Setup headless Tk root window
        self.root = tk.Tk()
        self.root.withdraw()  # Prevent window pop-up during tests

        # Use temporary in-memory database
        self.db = AlertDatabase(":memory:")
        self.alert_module = AlertModule(self.db)

        # Instantiate UserInterface with mock AlertModule
        self.ui = UserInterface(self.root, self.alert_module)
        self.ui.all_alerts = [
            (1, "A1", "ENGTEMP", "Critical", "Engine temp exceeded", "13:00:00", "Active", "✅ ❌"),
            (2, "A2", "PRESSURE", "Moderate", "Hydraulic pressure low", "13:10:00", "Active", "✅ ❌"),
            (3, "A3", "CABIN", "Advisory", "Cabin pressure low", "13:15:00", "Active", "✅ ❌"),
        ]

        # Mock GUI table for non-interactive testing
        self.ui.table = MagicMock()
        self.ui.table.get_children.return_value = [1, 2, 3]
        self.ui.table.item.side_effect = lambda rid, **_: {"values": self.ui.all_alerts[int(rid)-1]} if isinstance(rid, int) else None

    def tearDown(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass
