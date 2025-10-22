import pandas as pd
from pathlib import Path
import logging

class SensorIntegration():

    REQUIRED_COLS = ["timestamp", "sensor_id", "sensor_type", "value", "unit"]

    def __init__(self) -> None:
        self.data = pd.DataFrame | None = None

    def sensor(self):
        pass

    def read_csv(self, file_path: str) -> pd.DataFrame:
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        logging.info(f"Loading sensor data from: {file_path}")
        df = pd.read_csv(file)

        self.validate_data(df)
        df = self.clean_data(df)

        self.data=(df)
        logging.info(f"Sensor data loaded successfully with: {len(df)} records.")
        return df
    
    def validate_data(self, df: pd.DataFrame) -> None:
        missing = [col for col in self.REQUIRED_COLS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in sensor data: {', ' .join(missing)}")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in ["sensor_id", "sensor_type", "unit"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        df = df.replace({'': pd.NA, 'NA': pd.NA})
        df = df.dropna(subset=["sensor_id", "value", "timestamp"])

        df["value"] = pd.to_numeric(df["value"], errors='coerce')
        df = df.dropna(subset=["value"])

        return df
    
    def get_sensor_data(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("No sensor data has been loaded yet.")
        return self.data