# localgh

Agente que usa tu IA local (LM Studio) para gestionar issues de este repo en GitHub.

Flujo: semaforo (1 inferencia a la vez) -> lee issues -> LLM local (JSON estricto) -> validacion -> GitHub si hay red, o cola SQLite si no.

## Uso en tu Mac

```bash
git clone https://github.com/IA-melo/claudecode && cd claudecode
python -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -e .
cp .env.example .env
nano .env   # rellena GITHUB_TOKEN y LLM_MODEL
set -a; source .env; set +a

localgh doctor            # lista modelos de LM Studio, red, token, cola
localgh triage            # dry-run: muestra que haria
localgh triage --apply    # etiqueta y comenta de verdad
localgh sync              # envia lo que quedo en cola sin internet
localgh watch --apply --every 300   # revisa issues nuevos cada 5 min
```

LM Studio: carga Qwen 3.5 4B, ve a Developer > Start Server (puerto 1234) y copia el id del modelo que muestra `localgh doctor` en `LLM_MODEL`.

Token: fine-grained PAT limitado a este repo con permiso Issues (lectura/escritura). Nunca lo subas al repo.

Tests: `pip install -U pip && pip install -e .[dev] && pytest`

Los issues procesados reciben la etiqueta `triaged` y no se vuelven a tocar. Si `LLM_MODEL` esta vacio se usa el primer modelo de chat cargado.

## Preguntar estilo Jarvis

Desde la terminal:

    localgh ask como vamos

Desde el chat de LM Studio (Qwen llama a la herramienta `repo_status`): en LM Studio abre Program > Install > Edit mcp.json y agrega, cambiando la ruta y el token:

    {"mcpServers": {"localgh": {"command": "/RUTA/claudecode/.venv/bin/localgh", "args": ["mcp"], "env": {"GITHUB_TOKEN": "TU_TOKEN", "GITHUB_REPO": "IA-melo/claudecode"}}}}

Luego pregunta en el chat, por ejemplo: "como va el proyecto". Activa el servidor localgh en el chat.
