from __future__ import annotations

import json
import urllib.request


class GitHub:
    def __init__(self, token: str, repo: str):
        self.token, self.repo = token, repo

    def _req(self, method: str, path: str, body: dict | None = None):
        req = urllib.request.Request(
            f"https://api.github.com/repos/{self.repo}{path}",
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    def open_issues(self, limit: int = 20) -> list[dict]:
        items = self._req("GET", f"/issues?state=open&per_page={limit}")
        return [i for i in items if "pull_request" not in i]

    def comment(self, number: int, body: str):
        return self._req("POST", f"/issues/{number}/comments", {"body": body})

    def add_labels(self, number: int, labels: list[str]):
        return self._req("POST", f"/issues/{number}/labels", {"labels": labels})

    def recent_issues(self, limit: int = 15) -> list[dict]:
        items = self._req("GET", f"/issues?state=all&per_page={limit}")
        return [i for i in items if "pull_request" not in i]

    def commits(self, limit: int = 8) -> list[dict]:
        return self._req("GET", f"/commits?per_page={limit}")
