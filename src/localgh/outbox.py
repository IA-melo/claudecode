"""Cola local (SQLite) de acciones pendientes de enviar a GitHub."""
import json
import sqlite3


class Outbox:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS outbox ("
            "id INTEGER PRIMARY KEY, kind TEXT, payload TEXT, sent INTEGER DEFAULT 0)"
        )

    def add(self, kind: str, payload: dict):
        self.db.execute("INSERT INTO outbox(kind, payload) VALUES (?,?)", (kind, json.dumps(payload)))
        self.db.commit()

    def pending(self) -> list[tuple[int, str, dict]]:
        rows = self.db.execute("SELECT id, kind, payload FROM outbox WHERE sent=0 ORDER BY id")
        return [(i, k, json.loads(p)) for i, k, p in rows]

    def mark_sent(self, id_: int):
        self.db.execute("UPDATE outbox SET sent=1 WHERE id=?", (id_,))
        self.db.commit()
