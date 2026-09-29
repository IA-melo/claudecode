# localgh

Agente que usa tu IA local (Ollama) para gestionar issues de este repo en GitHub.

Flujo: semaforo (1 inferencia a la vez) -> lee issues -> LLM local (JSON estricto) -> validacion -> GitHub si hay red, o cola SQLite si no.

## Uso en tu Mac

```bash
git clone https://github.com/IA-melo/claudecode && cd claudecode
python -m venv .venv && source .venv/bin/activate && pip install -e .
cp .env.example .env   # rellena GITHUB_TOKEN; luego: set -a; source .env; set +a
ollama pull qwen3:4b

localgh doctor            # comprueba Ollama, red, token, cola
localgh triage            # dry-run: muestra que haria
localgh triage --apply    # etiqueta y comenta de verdad
localgh sync              # envia lo que quedo en cola sin internet
```

Token: fine-grained PAT limitado a este repo con permiso Issues (lectura/escritura). Nunca lo subas al repo.

Tests: `pip install -e .[dev] && pytest`
