# insight_project_microservice

FastAPI microservice that wraps [TaskJuggler 3](https://taskjuggler.org/) for
project scheduling. Used by the Odoo addon
[insight_project](https://github.com/csrocha/insight_project).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Verify tj3 is installed and responding |
| `POST` | `/schedule` | Run tj3 on TJP content, return CSV |

### `POST /schedule`

**Request body:**
```json
{
  "tjp_content": "<full .tjp file content>",
  "timeout": 120
}
```

**Response:**
```json
{
  "csv": "<DebugCSV.csv content>",
  "stdout": "<tj3 stdout>",
  "stderr": "<tj3 stderr>"
}
```

**Error codes:**
- `408` — tj3 timed out
- `422` — tj3 ran but produced no CSV (check TJP syntax errors in `detail.stderr`)

## Running locally

```bash
# With Docker Compose (recommended)
docker compose up

# Without Docker (requires tj3 and Python 3.11+)
pip install -r requirements-dev.txt
python main.py
```

## Running tests

```bash
# Inside Docker (tj3 available):
docker compose run --rm microservice pytest tests/ -v

# Locally (schedule tests auto-skipped if tj3 not installed):
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Building the image

```bash
docker build -t csrocha/tj3-ms .
docker run -p 8080:8080 csrocha/tj3-ms
```

## Deployment

The Docker image is built and deployed by the
[fop-odoo](https://github.com/observatoriopyme/fop-odoo) GitHub Actions workflows.
This repository contains only the application code.

## License

OPL-1 — Cristian S. Rocha <csrocha@gmail.com>
