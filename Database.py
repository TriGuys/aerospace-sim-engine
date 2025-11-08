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
                timestamp       TEXT    NOT NULL CHECK (timestamp GLOB '??:??:??'),
                status          TEXT    NOT NULL DEFAULT 'Active'
            )
            """
        )
        self._con.commit()

    @staticmethod # doesn't require the class, just simply a utility function.
    def _validate_timestamp(ts: str) -> None:
        hour_minute_second = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")
        if not hour_minute_second.match(ts):
            raise ValueError("timestamp must be valid 24-hour HH:MM:SS (00–23:59:59)")
        
    @staticmethod
    def _to_alert(row: sqlite3.Row) -> Alert:
        """Convert the status string from the DB back to enum"""
        data = dict(row)
        data["status"] = Status(data["status"])
        return Alert(**data)

    def create(self, alert: AlertCreation) -> Alert:
        """Insert a new alert into the database and return an Alert object."""
        self._validate_timestamp(alert.timestamp)
        try:
            row = self._con.execute(
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

            self._con.commit()
            return self._to_alert(row)
            
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Invalid alert data: {e}")

    def get(self, alert_id: int) -> Optional[Alert]:
        """Retrieve a single alert by ID."""
        row = self._con.execute(
            "SELECT alert_id, sensor_id, fault_code, severity, message, timestamp, status FROM alerts WHERE alert_id = ?", (alert_id,)
        ).fetchone()
        if row is None:
            return None
        
        return self._to_alert(row)
    
    def get_all(self) -> list[Alert]:
        """Retrieve all alerts from the database."""
        rows = self._con.execute(
            """
            SELECT alert_id, sensor_id, fault_code, severity, message, timestamp, status
            FROM alerts
            ORDER BY alert_id ASC;
            """
        ).fetchall()

        # Convert status string back to status enum for each record.
        alerts = []
        for r in rows:
            alerts.append(self._to_alert(r))
        return alerts

    def delete(self, alert_id: int) -> bool:
        """Delete an alert by ID."""
        try:
            cur = self._con.execute(
                "DELETE FROM alerts WHERE alert_id = ?",
                (alert_id,)
            )
            self._con.commit()
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
            self._con.commit()
            return cur.rowcount > 0
        except sqlite3.OperationalError as e:
            raise RuntimeError(f"Failed to update alert status: {e}")