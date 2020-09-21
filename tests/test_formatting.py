import sys
from subprocess import run, PIPE
from pathlib import Path


def test_formatting():
    root = Path(__file__).parent.parent
    resp = run(
        [sys.executable, "-m", "black", "--check", root, "--exclude=__version__.py"],
        stderr=PIPE,
    )

    if resp.returncode != 0:
        raise AssertionError(str(resp.stderr, "UTF-8", "ignore"))
