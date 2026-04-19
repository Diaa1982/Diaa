import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.config import get_settings


class ExecutionStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def initialize(self) -> None:
        with sqlite3.connect(self.settings.sqlite_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    task TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    rendered_prompt_preview TEXT NOT NULL,
                    error_text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def create(self, record: Dict[str, Any]) -> None:
        with sqlite3.connect(self.settings.sqlite_path) as conn:
            conn.execute(
                """
                INSERT INTO executions (
                    execution_id, agent_id, mode, status, task, context_json,
                    output_text, rendered_prompt_preview, error_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record['execution_id'],
                    record['agent_id'],
                    record['mode'],
                    record['status'],
                    record['task'],
                    json.dumps(record['context'], ensure_ascii=False),
                    record.get('output_text', ''),
                    record.get('rendered_prompt_preview', ''),
                    record.get('error_text', ''),
                    record['created_at'],
                    record['updated_at'],
                ),
            )
            conn.commit()

    def update(self, execution_id: str, **updates: Any) -> None:
        if not updates:
            return
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        sets = ', '.join(f"{key} = ?" for key in updates.keys())
        values = [json.dumps(v, ensure_ascii=False) if key == 'context' else v for key, v in updates.items()]
        with sqlite3.connect(self.settings.sqlite_path) as conn:
            conn.execute(f"UPDATE executions SET {sets} WHERE execution_id = ?", (*values, execution_id))
            conn.commit()

    def get(self, execution_id: str) -> Dict[str, Any] | None:
        with sqlite3.connect(self.settings.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM executions WHERE execution_id = ?', (execution_id,)).fetchone()
            return self._row_to_dict(row) if row else None

    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.settings.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                'SELECT * FROM executions ORDER BY created_at DESC LIMIT ?',
                (limit,),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            'execution_id': row['execution_id'],
            'agent_id': row['agent_id'],
            'mode': row['mode'],
            'status': row['status'],
            'task': row['task'],
            'context': json.loads(row['context_json']),
            'output_text': row['output_text'],
            'rendered_prompt_preview': row['rendered_prompt_preview'],
            'error_text': row['error_text'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        }


execution_store = ExecutionStore()
