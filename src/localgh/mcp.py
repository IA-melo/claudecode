"""Servidor MCP (stdio) para LM Studio: expone el estado del repo como herramienta."""
import json
import sys

from .context import gather

TOOL = {
    "name": "repo_status",
    "description": "Estado actual del repo de GitHub: issues, commits, cola offline y avance del proyecto. Usala para responder cualquier pregunta sobre como va el proyecto.",
    "inputSchema": {"type": "object", "properties": {}},
}


def handle(msg, cfg, gh, box):
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None
    if method == "initialize":
        result = {"protocolVersion": msg["params"].get("protocolVersion", "2024-11-05"),
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "localgh", "version": "0.1"}}
    elif method == "tools/list":
        result = {"tools": [TOOL]}
    elif method == "tools/call":
        result = {"content": [{"type": "text", "text": gather(cfg, gh, box)}]}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "no soportado"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve(cfg, gh, box):
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle(json.loads(line), cfg, gh, box)
        if out:
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()
