"""Regression: command-line scripts must not shadow Python standard modules."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_build_and_audit_cli_in_fresh_interpreters(tmp_path):
    generated = tmp_path / "decision.docx"
    commands = [
        [sys.executable, "scripts/build.py", "examples/briefs/official_decision.json", "--out", str(generated)],
        [sys.executable, "scripts/audit_docx.py", str(generated), "--type", "official_decision"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert generated.is_file() and generated.stat().st_size > 10000
