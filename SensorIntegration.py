import pandas as pd
from pathlib import Path
import logging
import os

class SensorIntegration():

    REQUIRED_COLS = ["timestamp", "sensor_id", "sensor_type", "value", "unit"]

    def __init__(self) -> None:
        self.data: pd.DataFrame | None = None

    def pass_sensor_data(self) -> None:
        """Placeholder method for passing sensor data to fault detection module."""
        pass

    def read_csv(self, file_path: str | os.PathLike[str]) -> pd.DataFrame:
        """
        Load and preprocess a CSV file containing sensor readings.
        
        Args:
            file_path (str): Path to the CSV file.
            
        Returns:
            pd.DataFrame: A cleaned and validated DataFrame ready for fault detection.
            
        Raises:
            FileNotFoundError: If the file path does not exist.
            ValueError: If required columns are missing or data is invalid.
        """

        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        logging.info(f"Loading sensor data from: {file_path}")
        df = pd.read_csv(file)

        self._validate_data(df)
        df = self._clean_data(df)

        self.data = df
        logging.info(f"Sensor data loaded successfully with: {len(df)} records.")
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> None:
        """Ensure the DataFrame contains all required columns."""
        missing: list[str] = [col for col in self.REQUIRED_COLS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in sensor data: {', ' .join(missing)}")

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the sensor data."""
        for col in ["sensor_id", "sensor_type", "unit"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        df = df.replace({"": pd.NA, " ": pd.NA, "NA": pd.NA})
        df = df.dropna(subset=["sensor_id", "value", "timestamp"])

        df["value"] = pd.to_numeric(df["value"], errors='coerce')
        df = df.dropna(subset=["value"])

        return df
    
    def get_sensor_data(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("No sensor data has been loaded yet.")
        return self.data