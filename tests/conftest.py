import subprocess
import pytest


def pytest_collection_modifyitems(items):
    """Skip schedule tests when tj3 is not installed locally."""
    try:
        subprocess.run(["tj3", "--version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        skip = pytest.mark.skip(reason="tj3 not installed — run tests inside Docker")
        for item in items:
            if "schedule" in item.nodeid:
                item.add_marker(skip)
