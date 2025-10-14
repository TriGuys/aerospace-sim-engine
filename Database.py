import sqlite3, datetime
from pathlib import Path

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
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  source          TEXT    NOT NULL,
                  severity        TEXT    NOT NULL,
                  message         TEXT    NOT NULL,
                  created_at      TEXT    NOT NULL DEFAULT (STRFTIME('%Y-%m-%dT%H:%M','now'))
                )
                """
            )