import re
import sqlite3
from pathlib import Path
from typing import Optional
from Abstractions import Alert, AlertCreation, Status

class AlertDatabase:

    def __init__(self, db_path: str = "alerts.db") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(self.db_path, check_same_thread=False)
        self._con.row_factory = sqlite3.Row
        self._init_table()

    def close(self) -> None:
        try:
            self._con.close()
        finally:
            self._con = None
    
    def _init_table(self) -> None:
        self._con.execute(
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
        self._con.commit()

    @staticmethod # doesn't require the class, just simply a utility function.
    def _validate_timestamp(ts: str) -> None:
        hour_minute_second = re.compile(r"^\d{2}:\d{2}:\d{2}$")
        if not hour_minute_second.match(ts):
            raise ValueError("timestamp must be HH:MM:SS")

    def create(self, alert: AlertCreation) -> Alert:
        """Insert a new alert into the database and return an Alert object."""
        self._validate_timestamp(alert.timestamp)
        try:
            row = self._con.execute(
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
        row = self._con.execute(
            "SELECT alert_id, sensor_id, fault_code, severity, message, timestamp FROM alerts WHERE alert_id = ?", (alert_id,)
        ).fetchone()
        if row is None:
            return None
        
        # Convert status string back to status enum.
        data = dict(row)
        data["status"] = Status(data["status"])
        return Alert(**data)
    
    def get_all(self):
        rows = self._con.execute(
            """
            SELECT alert_id, sensor_id, fault_code, severity, message, timestamp
            FROM alerts
            ORDER BY alert_id ASC
            """
        ).fetchall()
        return [Alert(**dict(r)) for r in rows]

    def delete(self, alert_id: int) -> bool:
        """Delete an alert by ID."""
        try:
            cur = self._con.execute(
                "DELETE FROM alerts WHERE alert_id = ?",
                (alert_id,)
            )
            return cur.rowcount > 0
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Delete failed: {e}")
        
    def update_status(self, alert_id: int, status: Status) -> bool:
        """Update the status (Active/Resolved) of an alert."""
        try:
            cur = self._con.execute(
                "UPDATE alerts SET status = ? WHERE alert_id = ?",
                (status.value, alert_id)
            )
            return cur.rowcount > 0
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Failed to update alert status: {e}")