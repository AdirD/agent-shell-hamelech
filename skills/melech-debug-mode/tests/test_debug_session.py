from __future__ import annotations

import argparse
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "debug_session.py"
SPEC = importlib.util.spec_from_file_location("debug_session", SCRIPT)
assert SPEC and SPEC.loader
debug_session = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(debug_session)


class LogsSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session_dir = Path(tempfile.mkdtemp(prefix=debug_session.SESSION_PREFIX))
        (self.session_dir / "launcher.json").write_text("{}\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.session_dir, ignore_errors=True)

    def write_events(self, events: list[dict[str, object]]) -> None:
        content = "".join(json.dumps(event, separators=(",", ":")) + "\n" for event in events)
        (self.session_dir / "events.jsonl").write_text(content, encoding="utf-8")

    def run_logs(
        self,
        *,
        run: str | None = None,
        after_seq: int = 0,
        tail: int = 200,
        pretty: bool = False,
    ) -> str:
        args = argparse.Namespace(
            session_dir=str(self.session_dir),
            run=run,
            after_seq=after_seq,
            tail=tail,
            pretty=pretty,
        )
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(debug_session.logs_session(args), 0)
        return output.getvalue()

    def test_default_output_is_one_complete_json_event_per_line(self) -> None:
        events = [
            {"seq": 1, "payload": {"run": "run-1", "probe": "before", "data": {"ok": True}}},
            {"seq": 2, "payload": {"run": "run-1", "probe": "after", "data": {"count": 2}}},
        ]
        self.write_events(events)

        lines = self.run_logs().splitlines()

        self.assertEqual([json.loads(line) for line in lines], events)
        self.assertEqual(len(lines), 2)

    def test_filters_before_applying_tail(self) -> None:
        events = [
            {"seq": 1, "payload": {"run": "run-1", "probe": "first"}},
            {"seq": 2, "payload": {"run": "run-2", "probe": "other"}},
            {"seq": 3, "payload": {"run": "run-1", "probe": "second"}},
            {"seq": 4, "payload": {"run": "run-1", "probe": "third"}},
        ]
        self.write_events(events)

        lines = self.run_logs(run="run-1", after_seq=1, tail=2).splitlines()

        self.assertEqual([json.loads(line)["seq"] for line in lines], [3, 4])

    def test_pretty_output_remains_available_for_humans(self) -> None:
        event = {"seq": 1, "payload": {"run": "run-1", "probe": "before"}}
        self.write_events([event])

        output = self.run_logs(pretty=True)

        self.assertGreater(len(output.splitlines()), 1)
        self.assertEqual(json.loads(output), event)

    def test_logs_cli_defaults_to_jsonl_and_accepts_pretty(self) -> None:
        parser = debug_session.build_parser()

        default_args = parser.parse_args(["logs", str(self.session_dir)])
        pretty_args = parser.parse_args(["logs", str(self.session_dir), "--pretty"])

        self.assertFalse(default_args.pretty)
        self.assertTrue(pretty_args.pretty)

    def test_invalid_jsonl_reports_the_source_line(self) -> None:
        (self.session_dir / "events.jsonl").write_text('{"seq":1}\nnot-json\n', encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "invalid JSONL at line 2"):
            self.run_logs()


if __name__ == "__main__":
    unittest.main()
