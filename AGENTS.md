# AGENTS.md — Directrices para Agentes de IA

**Repositorio**: `csrocha/insight_project_microservice`
**Propósito**: Microservicio FastAPI que ejecuta TaskJuggler 3 y devuelve el CSV de scheduling.
**Stack**: Python 3.11 + FastAPI + Ruby 3.2 + TJ3 gem, empaquetado en Docker.

## Invariantes del contrato de API

- `GET /health` siempre devuelve `{"status": "ok", "tj3_version": "..."}` si tj3 está disponible.
- `POST /schedule` recibe `{"tjp_content": str, "timeout": int}` y devuelve
  `{"csv": str, "stdout": str, "stderr": str}`.
- Si tj3 no produce CSV → HTTP 422 (nunca 500 para errores de TJP; 500 solo para
  errores de infraestructura).
- El campo `csv` contiene el contenido crudo del primer archivo `.csv` que tj3
  escriba en el directorio de salida (típicamente `DebugCSV.csv`).

## Checklist Pre-commit

- [ ] `main.py` no importa nada de GCP ni de proveedores cloud específicos.
- [ ] Los tests pasan dentro de Docker: `docker compose run --rm microservice pytest tests/`
- [ ] El `Dockerfile` construye sin errores: `docker build -t tj3-ms .`
- [ ] `CHANGELOG.md` tiene entrada para el cambio.

## Actualización de CHANGELOG (obligatorio)

Antes de cada commit, agregar una entrada en `CHANGELOG.md`.
Formato: `## [X.Y.Z] - YYYY-MM-DD` con secciones `Anadido / Modificado / Eliminado`.
