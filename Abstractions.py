from dataclasses import dataclass

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
import pandas as pd

class Reader(ABC):
    @abstractmethod
    def read(self) -> pd.DataFrame:
        raise NotImplementedError
    
class Validator(ABC):
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
    
class Preprocessor(ABC):
    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

class OutlierDetector(ABC):
    @abstractmethod
    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
    
class Pipeline(Protocol):
    def run(self) -> pd.DataFrame: ...
    @property
    def data(self) -> pd.DataFrame: ...

__all__ = [
    "Reader",  
    "Validator",
    "Preprocessor",
    "OutlierDetector",
    "Pipeline",
]

@dataclass(frozen=True)
class AlertCreation:
    sensor_id: str
    fault_code: str
    severity: str
    message: str
    timestamp: str

@dataclass(frozen=True)
class Alert:
    alert_id: int
    sensor_id: str
    fault_code: str
    severity: str
    message: str
    timestamp: str