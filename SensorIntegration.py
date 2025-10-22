import pandas as pd
from pathlib import Path
import logging

class SensorIntegration():

    def __init__(self):
        pass

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
    
