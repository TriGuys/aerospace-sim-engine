import sqlite3, datetime
from pathlib import Path

con = sqlite3.connect("alerts.db", detect_types=sqlite3.PARSE_DECLTYPES) # detect types is for datetime within the db


class db:

    def __init__(self, db_path: str = "alerts.db") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_table()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con