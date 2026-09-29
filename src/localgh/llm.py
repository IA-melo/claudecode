"""Cliente para servidores compatibles con OpenAI (LM Studio, Ollama /v1, etc.)."""
import json
import re
import urllib.request

SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "triage",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "labels": {"type": "array", "items": {"type": "string"}},
                "comment": {"type": "string"},
            },
            "required": ["labels", "comment"],
        },
    },
}


class LocalLLM:
    def __init__(self, url: str, model: str):
        self.url, self.model = url.rstrip("/"), model

    def _get(self, path: str):
        with urllib.request.urlopen(f"{self.url}{path}", timeout=5) as r:
            return json.load(r)

    def models(self) -> list[str]:
        try:
            return [m["id"] for m in self._get("/models")["data"]]
        except (OSError, KeyError, ValueError):
            return []

    def alive(self) -> bool:
        return bool(self.models())

    def chat(self, system: str, user: str) -> str:
        body = {
            "model": self.model,
            "temperature": 0,
            "response_format": SCHEMA,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        req = urllib.request.Request(
            f"{self.url}/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            text = json.load(r)["choices"][0]["message"]["content"] or ""
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
