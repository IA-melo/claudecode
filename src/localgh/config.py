import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    token: str
    repo: str
    ollama_url: str
    model: str
    db_path: str
    lock_path: str

    @classmethod
    def from_env(cls) -> "Config":
        e = os.environ.get
        return cls(
            token=e("GITHUB_TOKEN", ""),
            repo=e("GITHUB_REPO", "IA-melo/claudecode"),
            ollama_url=e("OLLAMA_URL", "http://localhost:11434").rstrip("/"),
            model=e("OLLAMA_MODEL", "qwen3:4b"),
            db_path=e("LOCALGH_DB", "localgh.db"),
            lock_path=e("LOCALGH_LOCK", "/tmp/localgh.lock"),
        )
