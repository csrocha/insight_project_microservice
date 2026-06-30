# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado: `MAYOR.MENOR.PARCHE`.

---

## [1.0.1] - 2026-06-30

### Corregido

- **Dockerfile**: agregado stage `test` (extiende `prod`) que instala `pytest` + `httpx`
  y copia `tests/` — el stage de producción no incluye dependencias de test.
- **ci.yml**: `docker build --target test` para la etapa de tests; `target: prod` en
  `build-push-action` para que la imagen publicada no lleve dependencias de test.

---

## [1.0.0] - 2026-06-30

### Prompt

> El paso 8 hay que hacerlo en otro repositorio. También en mi usuario de github
> sería el repositorio de nombre insight_project_microservice; deberías crearlo
> y luego dejar ahí el docker y los scripts fastapi, etc. No involucres nada de GCP.
> El deploy debería manejarlo fop-odoo en sus actions.

### Discusion de diseno

- **Un solo `main.py`, sin módulos extra**: el microservicio tiene una única
  responsabilidad (correr tj3 sobre TJP content). Un solo archivo evita overhead
  de packaging para algo tan acotado.
- **`glob` recursivo para encontrar el CSV**: tj3 puede crear el CSV directamente
  en el output dir o dentro de un subdirectorio con el nombre del proyecto (depende
  de la versión). `glob("**/*.csv", recursive=True)` es más robusto que hardcodear
  `DebugCSV.csv`.
- **HTTP 422 para TJP inválido, no 500**: 422 ("Unprocessable Entity") es más
  correcto semánticamente — el servidor procesó bien el request pero el contenido
  del TJP es inválido desde el punto de vista de tj3.
- **`PORT` env var sin dependencias de GCP**: cualquier plataforma de contenedores
  (Cloud Run, Railway, Fly.io, etc.) inyecta `PORT`. El `CMD` usa `${PORT:-8080}`
  con shell form para que sea agnóstico al proveedor.
- **`ruby:3.2-slim` como base**: TJ3 es un gem Ruby y necesita el runtime en
  producción. Se optó por instalar Python3 + venv sobre la imagen Ruby en lugar de
  la inversa porque TJ3 no se puede separar de su runtime en un multi-stage simple.
- **`docker-compose.yml` para desarrollo local**: permite levantar el servicio con
  `docker compose up` sin conocer los flags de `docker run`. No se incluye en la
  imagen final (está en `.dockerignore`).
- **`conftest.py` con skip condicional**: los tests de `/schedule` requieren tj3
  instalado. En lugar de fallar con `FileNotFoundError`, el conftest detecta la
  ausencia de tj3 y marca los tests como skip con mensaje claro.
- **Deploy gestionado desde `fop-odoo`**: este repo solo tiene el código de la app.
  Los workflows de GitHub Actions que construyen y despliegan la imagen viven en
  `fop-odoo` para centralizar la gestión de credenciales cloud.

### Anadido

- `main.py`: app FastAPI con endpoints `GET /health` y `POST /schedule`.
- `Dockerfile`: imagen `ruby:3.2-slim` + tj3 gem + Python 3 venv + FastAPI/uvicorn.
- `docker-compose.yml`: para desarrollo local.
- `.dockerignore`: excluye tests, README, archivos dev de la imagen.
- `requirements.txt` / `requirements-dev.txt`: dependencias prod y dev.
- `tests/conftest.py`: skip condicional si tj3 no está instalado.
- `tests/test_microservice.py`: tests de health check y schedule (válido/inválido).
- `AGENTS.md`: invariantes del contrato de API y checklist pre-commit.
