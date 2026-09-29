#!/usr/bin/env python3
"""Jarvis mínimo: servidor MCP (stdio) para LM Studio. Solo stdlib.

Herramientas: GitHub (issues), memoria y tareas personales.
Config por entorno: GITHUB_TOKEN, JARVIS_REPO (owner/repo), JARVIS_HOME (datos).
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path(os.environ.get("JARVIS_HOME", Path.home() / ".jarvis"))
DB = HOME / "data.json"
REPO = os.environ.get("JARVIS_REPO", "")


def load():
    try:
        return json.loads(DB.read_text())
    except Exception:
        return {"notes": [], "tasks": []}


def save(d):
    HOME.mkdir(parents=True, exist_ok=True)
    DB.write_text(json.dumps(d, ensure_ascii=False, indent=1))


def gh(path, method="GET", body=None):
    tok = os.environ.get("GITHUB_TOKEN")
    if not tok:
        return "Falta GITHUB_TOKEN"
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read() or "null")


def t_issues(state="open"):
    r = gh(f"/repos/{REPO}/issues?state={state}&per_page=30")
    if isinstance(r, str):
        return r
    return "\n".join(f"#{i['number']} [{i['state']}] {i['title']} "
                     f"({','.join(l['name'] for l in i['labels'])})"
                     for i in r if "pull_request" not in i) or "Sin issues."


def t_issue(number):
    i = gh(f"/repos/{REPO}/issues/{number}")
    return i if isinstance(i, str) else f"#{i['number']} {i['title']}\n{i['body'] or ''}"


def t_comment(number, text):
    gh(f"/repos/{REPO}/issues/{number}/comments", "POST", {"body": text})
    return "Comentario publicado."


def t_label(number, labels):
    gh(f"/repos/{REPO}/issues/{number}/labels", "POST", {"labels": labels})
    return "Etiquetas añadidas."


def t_remember(text):
    d = load()
    d["notes"].append({"t": time.strftime("%Y-%m-%d %H:%M"), "text": text})
    save(d)
    return "Guardado."


def t_recall(query=""):
    hits = [f"{n['t']} {n['text']}" for n in load()["notes"] if query.lower() in n["text"].lower()]
    return "\n".join(hits[-20:]) or "Nada."


def t_task_add(text):
    d = load()
    d["tasks"].append({"text": text, "done": False})
    save(d)
    return f"Tarea #{len(d['tasks'])} añadida."


def t_tasks():
    return "\n".join(f"{i+1}. [{'x' if t['done'] else ' '}] {t['text']}"
                     for i, t in enumerate(load()["tasks"])) or "Sin tareas."


def t_task_done(number):
    d = load()
    d["tasks"][int(number) - 1]["done"] = True
    save(d)
    return "Hecha."


def S(props=None, req=()):
    return {"type": "object", "properties": props or {}, "required": list(req)}


STR, INT = {"type": "string"}, {"type": "integer"}
TOOLS = {
    "github_issues": (t_issues, "Lista issues del repo (state: open|closed|all)", S({"state": STR})),
    "github_issue": (t_issue, "Lee un issue por número", S({"number": INT}, ["number"])),
    "github_comment": (t_comment, "Comenta en un issue", S({"number": INT, "text": STR}, ["number", "text"])),
    "github_label": (t_label, "Añade etiquetas a un issue",
                     S({"number": INT, "labels": {"type": "array", "items": STR}}, ["number", "labels"])),
    "remember": (t_remember, "Guarda una nota en la memoria personal", S({"text": STR}, ["text"])),
    "recall": (t_recall, "Busca en la memoria (vacío = últimas)", S({"query": STR})),
    "task_add": (t_task_add, "Añade una tarea", S({"text": STR}, ["text"])),
    "tasks": (t_tasks, "Lista las tareas", S()),
    "task_done": (t_task_done, "Marca una tarea como hecha", S({"number": INT}, ["number"])),
}


def handle(m):
    method, id_ = m.get("method"), m.get("id")
    if id_ is None:
        return None
    if method == "initialize":
        res = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
               "serverInfo": {"name": "jarvis", "version": "0.1"}}
    elif method == "tools/list":
        res = {"tools": [{"name": n, "description": d, "inputSchema": s}
                         for n, (_, d, s) in TOOLS.items()]}
    elif method == "tools/call":
        p = m["params"]
        try:
            out = str(TOOLS[p["name"]][0](**(p.get("arguments") or {})))
            res = {"content": [{"type": "text", "text": out}]}
        except Exception as e:
            res = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
    else:
        res = {}
    return {"jsonrpc": "2.0", "id": id_, "result": res}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            r = handle(json.loads(line))
            if r:
                print(json.dumps(r), flush=True)
