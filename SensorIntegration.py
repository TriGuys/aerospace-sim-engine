import pandas as pd
from pathlib import Path
import logging
import os

from Database import AlertDatabase

class SensorIntegration():

    REQUIRED_COLS = ["timestamp", "sensor_id", "sensor_type", "value", "unit"]

    def __init__(self) -> None:
        self.data: pd.DataFrame | None = None

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
            logging.error(f"File not found: {file_path}")
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
            logging.error(f"Missing required columns in sensor data: {', '.join(missing)}")
            raise ValueError(f"Missing required columns in sensor data: {', '.join(missing)}")

        duplicates = df.columns[df.columns.duplicated()].tolist()
        if duplicates:
            logging.error(f"Duplicate columns found in sensor data: {', '.join(duplicates)}")
            raise ValueError(f"Duplicate columns found in sensor data: {', '.join(duplicates)}")
        
        extra = [col for col in df.columns if col not in self.REQUIRED_COLS]
        if extra:
            logging.warning(f"Unexpected extra columns in sensor data: {', '.join(extra)}")
            raise ValueError(f"Unexpected extra columns in sensor data: {', '.join(extra)}")

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the sensor data."""
        try:
            for col in ["sensor_id", "sensor_type", "unit"]:
              if col in df.columns:
                   df[col] = df[col].astype(str).str.strip()

            df = df.replace({"": pd.NA, " ": pd.NA, "NA": pd.NA})
            df = df.dropna(subset=["sensor_id", "value", "timestamp"])

            df["value"] = pd.to_numeric(df["value"], errors='coerce')
            df = df.dropna(subset=["value"])

            # Reuse AlertDatabase's timestamp validation
            def _verify(ts: str) -> bool:
                try:
                    AlertDatabase._validate_timestamp(str(ts))
                    return True
                except ValueError:
                    return False
                
            bad_timestamps = ~df["timestamp"].astype(str).map(_verify)

            if bad_timestamps.any():
                logging.error("Invalid timestamp format detected: Expected HH:MM:SS.")
                raise ValueError("Invalid timestamp format detected: Expected HH:MM:SS.")

            return df
        
        except Exception as e:
            logging.error(f"Error during data cleaning: {e}")
            raise ValueError(f"Error during data cleaning: {e}")
    
    def get_sensor_data(self) -> pd.DataFrame:
        if self.data is None:
            logging.error("No sensor data has been loaded yet.")
            raise ValueError("No sensor data has been loaded yet.")
        return self.data