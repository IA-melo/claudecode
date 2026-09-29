import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    token: str
    repo: str
    llm_url: str
    model: str
    db_path: str
    lock_path: str

    @classmethod
    def from_env(cls) -> "Config":
        e = os.environ.get
        return cls(
            token=e("GITHUB_TOKEN", ""),
            repo=e("GITHUB_REPO", "IA-melo/claudecode"),
            llm_url=e("LLM_URL", "http://localhost:1234/v1").rstrip("/"),
            model=e("LLM_MODEL", ""),
            db_path=e("LOCALGH_DB", "localgh.db"),
            lock_path=e("LOCALGH_LOCK", "/tmp/localgh.lock"),
        )
