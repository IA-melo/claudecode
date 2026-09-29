import argparse
import sys

from . import agent
from .config import Config
from .gate import Busy, gate
from .github import GitHub
from .llm import Ollama
from .net import online
from .outbox import Outbox


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="localgh")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="comprueba Ollama, red y token")
    t = sub.add_parser("triage", help="clasifica y comenta issues abiertos")
    t.add_argument("--apply", action="store_true", help="escribir en GitHub (por defecto dry-run)")
    t.add_argument("--limit", type=int, default=5)
    sub.add_parser("sync", help="envia la cola pendiente")
    args = p.parse_args(argv)

    cfg = Config.from_env()
    gh, llm, box = GitHub(cfg.token, cfg.repo), Ollama(cfg.ollama_url, cfg.model), Outbox(cfg.db_path)

    if args.cmd == "doctor":
        print(f"ollama ({cfg.model}): {'ok' if llm.alive() else 'NO responde'}")
        print(f"internet: {'ok' if online() else 'sin conexion'}")
        print(f"token: {'definido' if cfg.token else 'FALTA GITHUB_TOKEN'}")
        print(f"pendientes en cola: {len(box.pending())}")
        return 0

    if args.cmd == "sync":
        if not online():
            print("sin conexion, nada que enviar")
            return 1
        print(f"enviados: {agent.flush(gh, box)}")
        return 0

    if not online():
        print("sin internet: no puedo leer issues")
        return 1
    for issue in gh.open_issues(args.limit):
        try:
            with gate(cfg.lock_path):
                result = agent.triage(llm, issue)
        except (Busy, agent.BadOutput) as e:
            print(f"#{issue['number']}: omitido ({e})")
            continue
        status = agent.deliver(gh, box, issue["number"], result, online=online(), apply=args.apply)
        print(f"#{issue['number']} [{status}] {result['labels']} {result['comment'][:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
