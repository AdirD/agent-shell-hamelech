from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "handoff.py"
SPEC = importlib.util.spec_from_file_location("melech_handoff", SCRIPT)
assert SPEC and SPEC.loader
handoff = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(handoff)


class HandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="melech-handoff-"))
        self.home = self.tmpdir / "home"
        self.worktree = self.tmpdir / "Users" / "demo" / "worktrees" / "feature-a"
        self.worktree.mkdir(parents=True)
        self.home.mkdir()
        self.env_patch = mock.patch.dict(
            os.environ,
            {
                "CURSOR_CONVERSATION_ID": "",
                "AGENT_TRANSCRIPTS": "",
                "CLAUDE_SESSION_ID": "",
                "CURSOR_DATA_DIR": "",
                "CLAUDE_CONFIG_DIR": "",
                "CODEX_HOME": "",
            },
            clear=False,
        )
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_cli(self, args: list[str], stdin: str = "") -> dict:
        buffer = io.StringIO()
        with mock.patch.object(handoff.sys, "stdin", io.StringIO(stdin)):
            with redirect_stdout(buffer):
                code = handoff.main([*args, "--cwd", str(self.worktree), "--home", str(self.home)])
        self.assertEqual(code, 0, buffer.getvalue())
        return json.loads(buffer.getvalue())

    def write_cursor(self, session_id: str, text: str, project: str | None = None) -> Path:
        slug = project or handoff.slug_path(self.worktree)
        path = (
            self.home
            / ".cursor"
            / "projects"
            / slug
            / "agent-transcripts"
            / session_id
            / f"{session_id}.jsonl"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"role": "user", "message": {"content": [{"type": "text", "text": text}]}})
            + "\n",
            encoding="utf-8",
        )
        return path

    def write_claude(self, session_id: str, text: str) -> Path:
        encoded = handoff.claude_slug(self.worktree)
        path = self.home / ".claude" / "projects" / encoded / f"{session_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"type": "user", "message": {"content": [{"type": "text", "text": text}]}})
            + "\n",
            encoding="utf-8",
        )
        return path

    def test_registry_has_forty_two_unique_rows(self) -> None:
        payload = self.run_cli(["providers"])
        ids = [row["id"] for row in payload["providers"]]
        self.assertEqual(payload["count"], 42)
        self.assertEqual(payload["full"], 26)
        self.assertEqual(payload["excluded"], 16)
        self.assertEqual(len(ids), len(set(ids)))
        for row in payload["providers"]:
            self.assertIn(row["support"], {"full", "excluded"})
            self.assertTrue(row.get("locations"))
            self.assertIn(row.get("unit"), {"file", "directory", "database"})
            if row["support"] == "excluded":
                self.assertTrue(row.get("excluded_reason"))
            else:
                self.assertFalse(row.get("excluded_reason"))

    def test_slug_uses_worktree_root(self) -> None:
        self.assertTrue(handoff.slug_path(self.worktree).endswith("Users-demo-worktrees-feature-a"))

    def test_age_label_is_compact_and_relative(self) -> None:
        self.assertEqual(handoff.age_label(12), "12s ago")
        self.assertEqual(handoff.age_label(8 * 60), "8m ago")
        self.assertEqual(handoff.age_label(3 * 60 * 60), "3h ago")
        self.assertEqual(handoff.age_label(2 * 24 * 60 * 60), "2d ago")

    def test_cursor_dotless_hidden_directory_slug_matches_worktree(self) -> None:
        worktree = Path("/Users/demo/.superset/worktrees/repo/feature-a")
        transcript = Path(
            "/Users/demo/.cursor/projects/"
            "Users-demo-superset-worktrees-repo-feature-a/"
            "agent-transcripts/session/session.jsonl"
        )
        self.assertTrue(handoff.matches_worktree(transcript, worktree))

    def test_expand_env_and_home(self) -> None:
        path = handoff.expand_template(
            "${CURSOR_DATA_DIR:-~/.cursor}/projects",
            {},
            self.home,
        )
        self.assertEqual(path, str(self.home / ".cursor" / "projects"))
        path = handoff.expand_template(
            "${CURSOR_DATA_DIR:-~/.cursor}/projects",
            {"CURSOR_DATA_DIR": "/tmp/alt-cursor"},
            self.home,
        )
        self.assertEqual(path, "/tmp/alt-cursor/projects")

    def test_list_reports_worktree_dates_and_transcript_stats(self) -> None:
        session = "1bc549f6-96f0-4d53-84d5-b138d46c51f0"
        transcript = self.write_cursor(session, "Investigate context usage.")
        records = [
            {
                "role": "user",
                "message": {
                    "content": (
                        "<timestamp>Tuesday</timestamp>"
                        "<user_query>Investigate context usage.</user_query>"
                    )
                },
            },
            {"role": "assistant", "message": {"content": "I will inspect it."}},
            {"role": "user", "message": {"content": "Compare the token totals too."}},
        ]
        transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

        listed = self.run_cli(["list"])
        self.assertEqual(listed["count"], 1)
        self.assertEqual(listed["worktree_name"], "feature-a")
        self.assertEqual(listed["rows"][0]["session_id"], session)
        self.assertEqual(listed["rows"][0]["worktree"], "feature-a")
        self.assertRegex(listed["rows"][0]["age"], r"^\d+[smhd] ago$")
        self.assertRegex(
            listed["rows"][0]["created"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
        )
        self.assertRegex(
            listed["rows"][0]["modified"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"
        )
        stats = listed["rows"][0]["stats"]
        self.assertTrue(stats["ok"])
        self.assertEqual(stats["messages"], 3)
        self.assertEqual(stats["user_messages"], 2)
        self.assertEqual(stats["chars"], len(transcript.read_text(encoding="utf-8")))
        self.assertEqual(stats["approx_tokens"], stats["chars"] // 4)
        self.assertEqual(listed["rows"][0]["topic"], "Investigate context usage.")
        self.assertEqual(
            listed["rows"][0]["glimpse"],
            "1. Investigate context usage.\n2. Compare the token totals too.",
        )

        looked = self.run_cli(["lookup", "--id", "1bc549f6"])
        self.assertEqual(looked["status"], "exact")
        self.assertEqual(looked["row"]["session_id"], session)
        self.assertEqual(looked["row"]["primary_transcript_path"], str(transcript.resolve()))
        self.assertNotIn("stats", looked["row"])
        self.assertNotIn("shape", looked["row"])

    def test_list_hides_current_cursor_session(self) -> None:
        current = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        other = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
        path = self.write_cursor(current, "current session")
        self.write_cursor(other, "prior session")
        with mock.patch.dict(
            os.environ,
            {
                "CURSOR_CONVERSATION_ID": current,
                "AGENT_TRANSCRIPTS": str(path.parent.parent),
            },
            clear=False,
        ):
            payload = self.run_cli(["list"])
        self.assertEqual([row["session_id"] for row in payload["rows"]], [other])

    def test_cursor_transcript_environment_works_when_home_is_unrelated(self) -> None:
        session = "cccccccc-cccc-cccc-cccc-cccccccccccc"
        path = self.write_cursor(session, "session found from transcript environment")
        sessions = handoff.discover_sessions(
            home=self.tmpdir / "unrelated-home",
            env={"AGENT_TRANSCRIPTS": str(path.parent.parent)},
            max_age_s=3600,
            now=path.stat().st_mtime + 1,
        )
        self.assertEqual([row["session_id"] for row in sessions], [session])

    def test_main_worktree_is_labeled_main(self) -> None:
        result = mock.Mock(
            returncode=0,
            stdout=f"worktree {self.worktree}\nHEAD abc123\nbranch refs/heads/main\n\n",
        )
        with mock.patch.object(handoff.subprocess, "run", return_value=result):
            self.assertEqual(handoff.worktree_label(self.worktree, self.worktree), "main")

    def test_session_directory_discovery(self) -> None:
        events = (
            self.home
            / ".copilot"
            / "session-state"
            / "abc123"
            / "events.jsonl"
        )
        events.parent.mkdir(parents=True, exist_ok=True)
        events.write_text(
            json.dumps({"type": "user", "text": "Continue from the checkout plan tomorrow"})
            + "\n",
            encoding="utf-8",
        )
        sessions = handoff.discover_sessions(
            home=self.home,
            env={},
            max_age_s=3600,
            now=events.stat().st_mtime + 1,
        )
        matches = [row for row in sessions if row["provider"] == "copilot_cli"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["session_id"], "abc123")
        self.assertEqual(
            matches[0]["glimpse"],
            "1. Continue from the checkout plan tomorrow",
        )

    def test_preview_uses_last_three_human_messages_and_ignores_claude_meta(self) -> None:
        transcript = self.write_claude("claude-session", "First human request")
        records = [
            {
                "type": "user",
                "message": {"role": "user", "content": "First human request"},
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": 'Example payload: {"role":"user","content":"not a user"}',
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "tool_result", "content": "tool output"}],
                },
            },
            {
                "type": "user",
                "isMeta": True,
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "image metadata"}],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Middle human request"}],
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Last human request"}],
                },
            },
        ]
        transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

        preview = handoff.extract_session_preview(transcript)
        self.assertEqual(preview["topic"], "First human request")
        self.assertEqual(
            preview["glimpse"],
            (
                "1. First human request\n"
                "2. Middle human request\n"
                "3. Last human request"
            ),
        )

    def test_glimpse_supports_whole_json_conversations(self) -> None:
        transcript = self.tmpdir / "conversation.json"
        transcript.write_text(
            json.dumps(
                {
                    "messages": [
                        {"role": "user", "content": "Start the migration"},
                        {"role": "assistant", "content": "Checking"},
                        {"role": "user", "content": "Preserve the audit log"},
                        {"role": "user", "content": "Keep the old IDs"},
                    ]
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        preview = handoff.extract_session_preview(transcript)
        self.assertEqual(preview["topic"], "Start the migration")
        self.assertEqual(
            preview["glimpse"],
            (
                "1. Start the migration\n"
                "2. Preserve the audit log\n"
                "3. Keep the old IDs"
            ),
        )

    def test_topic_skips_greetings_and_handoff_commands(self) -> None:
        transcript = self.tmpdir / "topic.jsonl"
        records = [
            {"role": "user", "content": "hi"},
            {"role": "user", "content": "/melech-handoff list"},
            {"role": "user", "content": "Improve the grouped session picker"},
            {"role": "user", "content": "Show the latest three per agent"},
        ]
        transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

        preview = handoff.extract_session_preview(transcript)
        self.assertEqual(preview["topic"], "Improve the grouped session picker")
        self.assertEqual(
            preview["glimpse"],
            (
                "1. /melech-handoff list\n"
                "2. Improve the grouped session picker\n"
                "3. Show the latest three per agent"
            ),
        )

    def test_glimpse_allows_160_chars_per_numbered_message(self) -> None:
        transcript = self.tmpdir / "long.jsonl"
        records = [
            {"role": "user", "content": "a" * 200},
            {"role": "user", "content": "b" * 200},
        ]
        transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

        first, last = handoff.extract_glimpse(transcript).splitlines()
        self.assertEqual(first, "1. " + ("a" * 159) + "…")
        self.assertEqual(last, "2. " + ("b" * 159) + "…")

    def test_excludes_sqlite_and_compressed_leaves(self) -> None:
        db = self.home / ".local" / "share" / "opencode" / "opencode.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        db.write_bytes(b"sqlite")
        compressed = self.home / ".codex" / "sessions" / "2026" / "01" / "01" / "rollout.jsonl.zst"
        compressed.parent.mkdir(parents=True, exist_ok=True)
        compressed.write_bytes(b"zstd")
        sessions = handoff.discover_sessions(
            home=self.home, env={}, max_age_s=3600, now=compressed.stat().st_mtime + 1
        )
        paths = [row["transcript_path"] for row in sessions]
        self.assertNotIn(str(db), paths)
        self.assertNotIn(str(compressed), paths)

    def test_claude_slug_matches_dotted_worktree(self) -> None:
        session = "4f9f41aa-6921-45c9-883f-e664386a205f"
        self.write_claude(session, "Why did debug mode skip manual verification")
        payload = self.run_cli(["list"])
        self.assertEqual(payload["rows"][0]["provider"], "claude_code")


if __name__ == "__main__":
    unittest.main()
