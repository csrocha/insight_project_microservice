"""
TJ3 Microservice — FastAPI wrapper around TaskJuggler 3.

Endpoints:
  GET  /health     → verify tj3 is reachable
  POST /schedule   → accept TJP content, run tj3, return CSV
"""
import glob
import logging
import os
import subprocess
import tempfile

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="TJ3 Microservice",
    description="TaskJuggler 3 scheduling microservice for Odoo insight_project",
    version="1.1.0",
)


# ── Models ────────────────────────────────────────────────────────────────────

class ScheduleRequest(BaseModel):
    tjp_content: str = Field(..., description="Full content of the .tjp project file")
    timeout: int = Field(120, ge=10, le=600, description="Max seconds to wait for tj3")


class ScheduleResponse(BaseModel):
    csv_files: dict = Field(..., description="Map of filename → CSV content for each taskreport")
    stdout: str
    stderr: str


class HealthResponse(BaseModel):
    status: str
    tj3_version: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health():
    """Check that tj3 is installed and responding."""
    try:
        result = subprocess.run(
            ["tj3", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail={"error": "tj3 not found", "hint": "Install with: gem install taskjuggler"},
        )
    if result.returncode != 0:
        raise HTTPException(
            status_code=503,
            detail={"error": "tj3 returned non-zero", "stderr": result.stderr},
        )
    return HealthResponse(status="ok", tj3_version=result.stdout.strip())


@app.post("/schedule", response_model=ScheduleResponse)
def schedule(req: ScheduleRequest):
    """Run tj3 on the supplied TJP content and return the CSV report."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tjp_path = os.path.join(tmpdir, "project.tjp")
        with open(tjp_path, "w", encoding="utf-8") as f:
            f.write(req.tjp_content)

        try:
            result = subprocess.run(
                ["tj3", "--output-dir", tmpdir, tjp_path],
                capture_output=True,
                text=True,
                timeout=req.timeout,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=408,
                detail={"error": f"tj3 timed out after {req.timeout}s"},
            )

        logger.info("tj3 exit=%d stdout=%s", result.returncode, result.stdout[:200])
        if result.returncode != 0:
            logger.warning("tj3 stderr: %s", result.stderr[:500])

        # TJ3 writes CSV files to the output dir (or a project-named subdirectory).
        # Collect all of them; Odoo maps each file back to its scenario.
        found = glob.glob(os.path.join(tmpdir, "**", "*.csv"), recursive=True)
        if not found:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "tj3 produced no CSV output — check TJP syntax",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            )

        csv_files = {}
        for path in found:
            filename = os.path.basename(path)
            with open(path, "r", encoding="utf-8") as f:
                csv_files[filename] = f.read()

        return ScheduleResponse(
            csv_files=csv_files,
            stdout=result.stdout,
            stderr=result.stderr,
        )


# ── Local dev entrypoint ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
