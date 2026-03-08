import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "bootstrap" / "scripts" / "pkb_task_start_agent.sh"


class PkbTaskStartAgentShellTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work_dir = Path(self.temp_dir.name)
        self.bin_dir = self.work_dir / "bin"
        self.bin_dir.mkdir()
        self.python3_args_file = self.work_dir / "python3-args.txt"

        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}:{env['PATH']}"
        env["TEST_REPO_SRC"] = str(REPO_ROOT)
        env["PYTHON3_ARGS_FILE"] = str(self.python3_args_file)
        self.env = env

        self._write_executable(
            "git",
            """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != "clone" ]]; then
  echo "unexpected git args: $*" >&2
  exit 1
fi
dst="${@: -1}"
mkdir -p "$(dirname "$dst")"
cp -R "$TEST_REPO_SRC" "$dst"
""",
        )
        self._write_executable(
            "codex",
            """#!/usr/bin/env bash
exit 0
""",
        )
        self._write_executable(
            "python3",
            """#!/usr/bin/env bash
set -euo pipefail
printf '%s\n---\n' "$@" >> "$PYTHON3_ARGS_FILE"
exit 0
""",
        )

    def _write_executable(self, name: str, content: str) -> None:
        path = self.bin_dir / name
        path.write_text(textwrap.dedent(content), encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def test_non_interactive_stdin_without_flag_fails_cleanly_before_python(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT_PATH)],
            cwd=str(REPO_ROOT),
            env=self.env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stdin is not interactive", result.stderr)
        self.assertIn("--no-interactive --task", result.stderr)
        args = self.python3_args_file.read_text(encoding="utf-8")
        self.assertIn("update_skills_mirror.py", args)
        self.assertNotIn("pkb_task_start_agent.py", args, "bootstrap entrypoint should not be invoked")

    def test_no_interactive_mode_passes_flags_to_python(self) -> None:
        result = subprocess.run(
            [
                "bash",
                str(SCRIPT_PATH),
                "--no-interactive",
                "--task",
                "bootstrap skills",
                "--done",
                "agents file updated",
            ],
            cwd=str(REPO_ROOT),
            env=self.env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        args = self.python3_args_file.read_text(encoding="utf-8")
        self.assertIn("update_skills_mirror.py", args)
        self.assertIn("--no-interactive", args)
        self.assertIn("--task", args)
        self.assertIn("bootstrap skills", args)
        self.assertIn("--done", args)
        self.assertIn("agents file updated", args)


if __name__ == "__main__":
    unittest.main()
