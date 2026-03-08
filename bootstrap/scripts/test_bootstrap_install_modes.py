import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HUMAN_SCRIPT = REPO_ROOT / "bootstrap" / "scripts" / "pkb_task_start.sh"


class AgentInstallLibTests(unittest.TestCase):
    def test_import_and_destinations(self) -> None:
        from bootstrap.scripts import pkb_install_lib

        target = Path("/tmp/example-project")
        self.assertEqual(pkb_install_lib.copy_install_root(target, "codex"), target / ".codex" / "skills")
        self.assertEqual(pkb_install_lib.copy_install_root(target, "claude"), target / ".claude" / "skills")
        self.assertEqual(pkb_install_lib.copy_install_root(target, "agents"), target / ".agents" / "skills")
        self.assertEqual(pkb_install_lib.copy_install_root(target, "agent"), target / ".agent" / "skills")
        self.assertEqual(pkb_install_lib.copy_install_root(target, "kimi"), target / ".agents" / "skills")

    def test_kimi_prefers_existing_project_specific_dir(self) -> None:
        from bootstrap.scripts import pkb_install_lib

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".kimi" / "skills").mkdir(parents=True)
            self.assertEqual(pkb_install_lib.copy_install_root(target, "kimi"), target / ".kimi" / "skills")

    def test_detect_installed_agents_prefers_project_dirs(self) -> None:
        from bootstrap.scripts import pkb_install_lib

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".claude" / "skills").mkdir(parents=True)

            def fake_which(cmd: str) -> str | None:
                if cmd == "codex":
                    return "/usr/bin/codex"
                return None

            detected = pkb_install_lib.detect_installed_agents(target=target, which=fake_which)
            self.assertEqual(detected[0], "claude")
            self.assertIn("codex", detected)


class HumanSelectedBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work_dir = Path(self.temp_dir.name)
        self.bin_dir = self.work_dir / "bin"
        self.bin_dir.mkdir()
        self.target_dir = self.work_dir / "target"
        self.target_dir.mkdir()

        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}:{env['PATH']}"
        env["TEST_REPO_SRC"] = str(REPO_ROOT)
        env["REAL_GIT"] = subprocess.run(
            ["bash", "-lc", "command -v git"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.env = env

        self._write_executable(
            "git",
            """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" != "clone" ]]; then
  "$REAL_GIT" "$@"
  exit $?
fi
dst="${@: -1}"
mkdir -p "$(dirname "$dst")"
cp -R "$TEST_REPO_SRC" "$dst"
""",
        )

    def _write_executable(self, name: str, content: str) -> None:
        path = self.bin_dir / name
        path.write_text(textwrap.dedent(content), encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def test_human_selected_noninteractive_copy_mode_installs_to_selected_agent_dir(self) -> None:
        result = subprocess.run(
            [
                "bash",
                str(HUMAN_SCRIPT),
                "--target",
                str(self.target_dir),
                "--agent",
                "claude",
                "--install-mode",
                "copy",
                "--no-interactive",
                "--task",
                "plan install workflow",
                "--done",
                "skills installed and AGENTS updated",
                "--constraints",
                "prefer minimal skills",
                "--skills",
                "uv-brainstorming uv-writing-plans",
            ],
            cwd=str(REPO_ROOT),
            env=self.env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue((self.target_dir / "AGENTS.md").exists(), "AGENTS.md should be created")
        self.assertTrue((self.target_dir / ".claude" / "skills" / "uv-brainstorming" / "SKILL.md").exists())
        self.assertTrue((self.target_dir / ".claude" / "skills" / "uv-writing-plans" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
