"""Reune los datos del repo (issues, commits, cola, estado) para responder preguntas."""
from .net import online

STATUS_HINT = "estado del proyecto"


def gather(cfg, gh, box) -> str:
    lines = [f"Repo: {cfg.repo}", f"Internet: {'ok' if online() else 'sin conexion'}",
             f"Acciones pendientes en cola offline: {len(box.pending())}"]
    if not online():
        lines.append("(sin internet: solo datos locales)")
        return "\n".join(lines)
    try:
        issues = gh.recent_issues()
        for i in issues:
            tags = ",".join(l["name"] for l in i["labels"]) or "sin etiquetas"
            lines.append(f"Issue #{i['number']} [{i['state']}] {i['title']} ({tags})")
            if STATUS_HINT in i["title"].lower() and i["state"] == "open":
                lines.append(f"  Detalle: {(i.get('body') or '')[:1500]}")
        for c in gh.commits():
            lines.append(f"Commit {c['sha'][:7]}: {c['commit']['message'].splitlines()[0]}")
    except OSError as e:
        lines.append(f"(no pude leer GitHub: {e})")
    return "\n".join(lines)
