import os
import re
import pytest


@pytest.fixture(autouse=True)
def disable_color_env():
    """
    Ensure colored output is disabled for all tests so help text assertions
    (and other exact string checks) are deterministic regardless of environment.
    """
    os.environ.setdefault("NO_COLOR", "1")
    yield


def strip_ansi(s: str) -> str:
    """Optional helper to strip ANSI escape sequences in tests if needed."""
    return re.sub(r"\x1b\[[0-9;]*m", "", s)
