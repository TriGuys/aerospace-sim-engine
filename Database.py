import sqlite3, datetime
from pathlib import Path
from Abstractions import Alert, AlertCreation

con = sqlite3.connect("alerts.db", detect_types=sqlite3.PARSE_DECLTYPES) # detect types is for datetime within the db

class db:

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

    def create(self, alert: AlertCreation) -> int:
        with self._connect() as con:
            cur = con.execute(
                "INSERT INTO alerts(sensord_id,fault_code,severity,message,timestamp) VALUES (?,?,?,?,?)",
                (alert.sensor_id,
                 alert.fault_code,
                 alert.severity,
                 alert.message,
                 alert.timestamp)
            )
            con.commit()
            return cur.lastrowid

    def get(self, alertId):
        with self._connect() as con:
            row = con.execute(
                "SELECT alert_id, sensor_id, fault_code, severity, message, timestamp FROM alerts WHERE alert_id = ?", (alertId)
            ).fetchone()
            if not row: return None
            return Alert(row)
    
    def get_all(self):
        with self._connect() as con:
            con.row_factory = sqlite3.Row
            cur = con.execute("""
                SELECT alert_id, sensor_id, fault_code, severity, message, timestamp
                FROM alerts
                ORDER BY alert_id DESC
            """)
            return [
                Alert(
                    alert_id=r["alert_id"],
                    sensor_id=r["sensor_id"],
                    fault_code=r["fault_code"],
                    severity=r["severity"],
                    message=r["message"],
                    timestamp=r["timestamp"],
                )
                for r in cur.fetchall()
            ]