# Jarvis mínimo

Un archivo (`jarvis.py`, sin dependencias) que conecta tu Qwen en LM Studio con GitHub y una memoria personal.

Herramientas: `github_issues`, `github_issue`, `github_comment`, `github_label`, `remember`, `recall`, `task_add`, `tasks`, `task_done`.

## Instalar (Mac)

1. Clona el repo y anota la ruta absoluta de `jarvis.py`.
2. En LM Studio: Program → Install → Edit `mcp.json`:

```json
{
  "mcpServers": {
    "jarvis": {
      "command": "python3",
      "args": ["/RUTA/ABSOLUTA/jarvis.py"],
      "env": {
        "GITHUB_TOKEN": "TU_TOKEN_FINE_GRAINED",
        "JARVIS_REPO": "IA-melo/claudecode"
      }
    }
  }
}
```

Usa un token fine-grained limitado a este repo (Issues: read/write).

3. System prompt sugerido para Qwen:

> Eres Jarvis, asistente personal. Responde en español y breve. Usa las herramientas para consultar GitHub, guardar notas (`remember`) y gestionar tareas. Nunca inventes datos: si no lo sabes, llama a una herramienta.

Los datos personales quedan en `~/.jarvis/data.json`.
