from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cost.py"
SPEC = importlib.util.spec_from_file_location("melech_cost", SCRIPT)
assert SPEC and SPEC.loader
cost = importlib.util.module_from_spec(SPEC)
sys.modules["melech_cost"] = cost
SPEC.loader.exec_module(cost)


def git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=cwd, check=True, capture_output=True,
    )


class CostTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="melech-cost-")))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.main = self.tmp / "code" / "acme"
        self.main.mkdir(parents=True)
        git(self.main, "init", "-q")
        (self.main / "README.md").write_text("x\n")
        git(self.main, "add", ".")
        git(self.main, "commit", "-qm", "init")
        self.container = self.tmp / "worktrees" / "acme-project"
        self.container.mkdir(parents=True)
        self.feature = self.container / "feature-a"
        git(self.main, "worktree", "add", "-q", str(self.feature), "-b", "feature-a")
        self.sibling = self.tmp / "code" / "acme-web"
        self.sibling.mkdir()
        git(self.sibling, "init", "-q")
        self.env = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": "", "CODEX_HOME": "", "APPDATA": ""})
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cursor_transcript(self, path: Path, sid: str, prompt: str, calls: int = 3) -> None:
        slug = cost.path_slug(path)
        target = self.home / ".cursor" / "projects" / slug / "agent-transcripts" / sid / f"{sid}.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = [{"role": "user", "message": {"content": [{"type": "text", "text": f"<user_query>{prompt}</user_query>"}]}}]
        for _ in range(calls):
            lines.append({"role": "assistant", "message": {"content": [
                {"type": "text", "text": "thinking about it " * 20},
                {"type": "tool_use", "name": "Read", "input": {"path": "a.py"}},
            ]}})
        target.write_text("\n".join(json.dumps(l) for l in lines) + "\n")

    def claude_session(self, cwd: Path, sid: str, usage: dict, model: str = "claude-opus-5") -> None:
        target = self.home / ".claude" / "projects" / cost.path_slug(cwd) / f"{sid}.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            {"type": "user", "cwd": str(cwd), "timestamp": "2026-09-01T10:00:00Z",
             "message": {"role": "user", "content": "fix the flaky test"}},
            {"type": "assistant", "cwd": str(cwd), "timestamp": "2026-09-01T10:00:05Z",
             "message": {"id": "msg_1", "model": model, "usage": usage, "content": []}},
            {"type": "assistant", "cwd": str(cwd), "timestamp": "2026-09-01T10:00:05Z",
             "message": {"id": "msg_1", "model": model, "usage": usage, "content": []}},
        ]
        target.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    def codex_session(self, cwd: Path, sid: str) -> None:
        target = self.home / ".codex" / "sessions" / "2026" / "09" / "02" / f"rollout-{sid}.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            {"type": "session_meta", "timestamp": "2026-09-02T09:00:00Z", "payload": {"id": sid, "cwd": str(cwd)}},
            {"type": "turn_context", "payload": {"model": "gpt-5.4", "cwd": str(cwd)}},
            {"type": "event_msg", "payload": {"type": "user_message", "message": "ship the migration"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {
                "input_tokens": 1_000_000, "cached_input_tokens": 800_000, "output_tokens": 10_000}}}},
        ]
        target.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    def sessions(self) -> list[dict]:
        scope = cost.build_scope(self.feature)
        assert scope is not None
        return cost.collect(self.home, scope, 0.0)

    def test_scope_covers_main_worktrees_and_removed_but_not_sibling_repo(self) -> None:
        self.cursor_transcript(self.main, "s-main", "plan the release")
        self.cursor_transcript(self.feature, "s-feat", "build feature a")
        self.cursor_transcript(self.container / "old-branch", "s-old", "old work")
        self.cursor_transcript(self.sibling, "s-web", "unrelated repo")
        labels = {s["sid"]: s["worktree"] for s in self.sessions()}
        self.assertEqual(labels, {"s-main": "main", "s-feat": "feature-a", "s-old": "old-branch (removed)"})

    def test_claude_uses_logged_tokens_once_per_message(self) -> None:
        usage = {"input_tokens": 1000, "cache_creation_input_tokens": 2000,
                 "cache_read_input_tokens": 100_000, "output_tokens": 500}
        self.claude_session(self.feature, "c1", usage)
        [s] = self.sessions()
        expected = (1000 * 5 + 2000 * 6.25 + 100_000 * 0.5 + 500 * 25) / 1e6
        self.assertTrue(s["exact"])
        self.assertAlmostEqual(s["cost"], expected)
        self.assertEqual(s["worktree"], "feature-a")
        self.assertEqual(s["topic"], "fix the flaky test")

    def test_codex_prices_cached_input_separately(self) -> None:
        self.codex_session(self.main, "x1")
        [s] = self.sessions()
        self.assertAlmostEqual(s["cost"], (200_000 * 2.5 + 800_000 * 0.25 + 10_000 * 15) / 1e6)
        self.assertEqual(s["topic"], "ship the migration")

    def test_price_rules_pick_specific_before_generic(self) -> None:
        self.assertEqual(cost.price("claude-opus-5-5")["input"], 4)
        self.assertEqual(cost.price("claude-opus-4-7-fast")["input"], 30)
        self.assertEqual(cost.price("gpt-5.6-sol-fast")["input"], 8)
        self.assertEqual(cost.price("composer-2.5")["pool"], "cursor")
        self.assertEqual(cost.price("auto")["pool"], "assumed")

    def test_replay_bills_cached_prefix_on_later_calls(self) -> None:
        r = cost.replay([("in", 4000), ("call", 400), ("in", 4000), ("call", 400)], "claude-opus-5", 10_000, 10**9)
        self.assertEqual(r["calls"], 2)
        self.assertAlmostEqual(r["input_cached"], 11_000)
        self.assertGreater(r["cost"], 0)

    def test_cli_prints_cards_and_writes_full_report(self) -> None:
        self.cursor_transcript(self.feature, "s-feat", "build feature a")
        report = self.tmp / "report.md"
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cost.main(["--cwd", str(self.main), "--home", str(self.home), "--report", str(report)])
        self.assertEqual(code, 0)
        out = buf.getvalue()
        self.assertIn("## `acme` agent spend", out)
        self.assertIn("### `feature-a` ·", out)
        self.assertIn("`s-feat` · cursor · build feature a", out)
        self.assertTrue(report.read_text().startswith("## `acme`"))


if __name__ == "__main__":
    unittest.main()
