import re
import sqlite3
from pathlib import Path
from typing import Optional
from Abstractions import Alert, AlertCreation, Status

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
                  timestamp       TEXT    NOT NULL CHECK (timestamp GLOB '??:??:??'),
                  status          TEXT    NOT NULL DEFAULT 'Active'
                )
                """
            )

    @staticmethod # doesn't require the class, just simply a utility function.
    def _validate_timestamp(ts: str) -> None:
        hour_minute_second = re.compile(r"^\d{2}:\d{2}:\d{2}$")
        if not hour_minute_second.match(ts):
            raise ValueError("timestamp must be HH:MM:SS")

    def create(self, alert: AlertCreation) -> Alert:
        """Insert a new alert into the database and return an Alert object."""
        self._validate_timestamp(alert.timestamp)
        try:
            with self._connect() as con:
                row = con.execute(
                    """
                    INSERT INTO alerts(sensor_id, fault_code, severity, message, timestamp, status) 
                    VALUES (?,?,?,?,?,?)
                    RETURNING alert_id, sensor_id, fault_code, severity, message, timestamp, status
                    """,
                    (
                    alert.sensor_id,
                    alert.fault_code,
                    alert.severity,
                    alert.message,
                    alert.timestamp,
                    Status.ACTIVE.value
                    ),
                ).fetchone()

                # Convert the status string from the DB back to enum
                data = dict(row)
                data["status"] = Status(data["status"])
                return Alert(**data)
            
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Invalid alert data: {e}")

    def get(self, alert_id: int) -> Optional[Alert]:
        """Retrieve a single alert by ID."""
        with self._connect() as con:
            row = con.execute(
                "SELECT alert_id, sensor_id, fault_code, severity, message, timestamp, status FROM alerts WHERE alert_id = ?", (alert_id,)
            ).fetchone()
        if row is None:
            return None
        
        # Convert status string back to status enum.
        data = dict(row)
        data["status"] = Status(data["status"])
        return Alert(**data)
    
    def get_all(self):
        """Retrieve all alerts from the database."""
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT alert_id, sensor_id, fault_code, severity, message, timestamp, status
                FROM alerts
                ORDER BY alert_id ASC;
                """
            ).fetchall()

        # Convert status string back to status enum for each record.
        alerts = []
        for r in rows:
            data = dict(r)
            data["status"] = Status(data["status"])
            alerts.append(Alert(**data))
        return alerts

    def delete(self, alert_id: int) -> bool:
        """Delete an alert by ID."""
        try:
            with self._connect() as con:
                cur = con.execute(
                    "DELETE FROM alerts WHERE alert_id = ?",
                    (alert_id,)
                )
                return cur.rowcount > 0
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Delete failed: {e}")
        
    def update_status(self, alert_id: int, status: Status) -> bool:
        """Update the status (Active/Resolved) of an alert."""
        try:
            with self._connect() as con:
                cur = con.execute(
                    "UPDATE alerts SET status = ? WHERE alert_id = ?",
                    (status.value, alert_id)
                )
                return cur.rowcount > 0
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Failed to update alert status: {e}")