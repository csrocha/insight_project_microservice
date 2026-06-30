# ── Stage: production ─────────────────────────────────────────────────────────
FROM ruby:3.2-slim AS prod

# Install TaskJuggler gem (tj3 CLI)
RUN gem install taskjuggler --no-document

# Install Python 3 + pip + venv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Isolated venv avoids conflicts with system Python packages on Debian
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ── App ───────────────────────────────────────────────────────────────────────
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8080

# PORT env var is honoured by platforms that inject it (e.g. Cloud Run, Railway).
# Defaults to 8080 so plain `docker run` works without extra flags.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]

# ── Stage: test (not pushed to registry) ──────────────────────────────────────
FROM prod AS test
RUN pip install --no-cache-dir pytest httpx
COPY tests/ tests/
