import re
import sqlite3
from pathlib import Path
from typing import Optional
from Abstractions import Alert, AlertCreation

class AlertDatabase:

    def __init__(self, db_path: str = "alerts.db") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True) # make database file if it doesn't exist
        self._init_table()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con
    
    def _init_table(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                  alert_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                  sensor_id       TEXT    NOT NULL,
                  fault_code      TEXT    NOT NULL,
                  severity        TEXT    NOT NULL,
                  message         TEXT    NOT NULL,
                  timestamp       TEXT    NOT NULL CHECK (timestamp GLOB '??:??:??')
                )
                """
            )

    @staticmethod # doesn't require the class, just simply a utility function.
    def _validate_timestamp(ts: str) -> None:
        hour_minute_second = re.compile(r"^\d{2}:\d{2}:\d{2}$")
        if not hour_minute_second.match(ts):
            raise ValueError("timestamp must be HH:MM:SS")

    def create(self, alert: AlertCreation) -> Alert:
        self._validate_timestamp(alert.timestamp)
        try:
            with self._connect() as con:
                row = con.execute(
                    """
                    INSERT INTO alerts(sensor_id,fault_code,severity,message,timestamp) 
                    VALUES (?,?,?,?,?)
                    RETURNING alert_id, sensor_id, fault_code, severity, message, timestamp
                    """,
                    (
                    alert.sensor_id,
                    alert.fault_code,
                    alert.severity,
                    alert.message,
                    alert.timestamp
                    ),
                ).fetchone()
                return Alert(**dict(row))
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Invalid alert data: {e}")

    def get(self, alert_id: int) -> Optional[Alert]:
        with self._connect() as con:
            row = con.execute(
                "SELECT alert_id, sensor_id, fault_code, severity, message, timestamp FROM alerts WHERE alert_id = ?", (alert_id,)
            ).fetchone()
        if row is None:
            return None
        return Alert(**dict(row))
    
    def get_all(self):
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT alert_id, sensor_id, fault_code, severity, message, timestamp
                FROM alerts
                ORDER BY alert_id DESC
                """
            ).fetchall()
        return [Alert(**dict(r)) for r in rows]

    def delete(self, alert_id: int) -> bool:
        try:
            with self._connect() as con:
                cur = con.execute(
                    "DELETE FROM alerts WHERE alert_id = ?",
                    (alert_id,)
                )
                return cur.rowcount > 0
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Delete failed: {e}")