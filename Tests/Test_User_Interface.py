import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from pathlib import Path
import pandas as pd
import tkinter as tk

from Test_Base import TestBase
from UserInterface import UserInterface
from Database import AlertDatabase
from AlertModule import AlertModule

class TestUserInterface(TestBase):
    pass
