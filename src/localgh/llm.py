"""Cliente para servidores compatibles con OpenAI (LM Studio, Ollama /v1, etc.)."""
import json
import os
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
        self.last: dict = {}

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
            "max_tokens": 2048,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user + "\n/no_think"},
            ],
        }
        if os.environ.get("LLM_STRUCTURED") == "1":
            body["response_format"] = SCHEMA
        req = urllib.request.Request(
            f"{self.url}/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            self.last = json.load(r)
        text = self.last["choices"][0]["message"].get("content") or ""
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
        text = re.sub(r"<think>.*", "", text, flags=re.S)
        m = re.search(r"\{.*\}", text, flags=re.S)
        return m.group(0) if m else text.strip()


def pick_model(models: list[str]) -> str:
    chat = [m for m in models if "embed" not in m.lower()]
    return chat[0] if chat else ""
