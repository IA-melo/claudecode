import json
import urllib.request


class Ollama:
    def __init__(self, url: str, model: str):
        self.url, self.model = url, model

    def chat(self, system: str, user: str) -> str:
        body = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        req = urllib.request.Request(
            f"{self.url}/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)["message"]["content"]

    def alive(self) -> bool:
        try:
            urllib.request.urlopen(f"{self.url}/api/tags", timeout=3).close()
            return True
        except OSError:
            return False
