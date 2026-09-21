"""Tests fuer die Fertigmeldungs-Benachrichtigung (BRIDGE-0069).

Hermetisch: Fake-Notifier und Fake-Runner, kein echter Toast, kein echter Pull.
"""

import hashlib
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import yaml  # noqa: E402

from bridge import cli as cli_mod  # noqa: E402
from bridge import notify  # noqa: E402
from bridge.store import Store  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "schemas"
WAITING = "WAITING_FOR_COPY_TO_CONTROL"


class NewEntriesTests(unittest.TestCase):
    def test_detects_only_new_ids_sorted(self):
        got = notify.new_entries({"BRIDGE-1"}, {"BRIDGE-3": "c", "BRIDGE-1": "a", "BRIDGE-2": "b"})
        self.assertEqual(got, [("BRIDGE-2", "b"), ("BRIDGE-3", "c")])

    def test_nothing_new(self):
        self.assertEqual(notify.new_entries({"A"}, {"A": "x"}), [])
        self.assertEqual(notify.new_entries(set(), {}), [])


class CompletionWatcherTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        self.calls = []
        self.notifier = lambda tid, title: self.calls.append((tid, title))

    def watcher(self):
        return notify.CompletionWatcher(lambda: dict(self.state), self.notifier)

    def test_old_stock_is_silent(self):
        self.state = {"BRIDGE-1": "alt"}
        w = self.watcher()
        w()
        w()
        self.assertEqual(self.calls, [])

    def test_new_entry_reported_once(self):
        w = self.watcher()
        self.state["BRIDGE-2"] = "neu"
        w()
        w()  # unveraendert: keine zweite Meldung (Entprellung)
        self.assertEqual(self.calls, [("BRIDGE-2", "neu")])

    def test_reentry_after_leaving_reports_again(self):
        w = self.watcher()
        self.state["BRIDGE-2"] = "neu"
        w()
        del self.state["BRIDGE-2"]
        w()
        self.state["BRIDGE-2"] = "neu"
        w()
        self.assertEqual(self.calls, [("BRIDGE-2", "neu")] * 2)

    def test_notifier_exception_is_fail_open(self):
        def boom(tid, title):
            raise RuntimeError("kaputt")

        w = notify.CompletionWatcher(lambda: dict(self.state), boom)
        self.state = {"BRIDGE-1": "a", "BRIDGE-2": "b"}
        err = StringIO()
        with redirect_stderr(err):
            w()  # darf nicht werfen
        self.assertIn("kaputt", err.getvalue())
        with redirect_stderr(StringIO()):
            w()  # Basis wurde trotzdem aktualisiert
        self.assertEqual(self.calls, [])


class ToastNotifierTests(unittest.TestCase):
    def make(self, platform="win32", runner=None, timeout=7):
        self.runner = runner or mock.Mock(return_value=mock.Mock(returncode=0))
        return notify.PowerShellToastNotifier(
            runner=self.runner, platform=platform, timeout=timeout, environ={"X": "1"})

    def test_non_windows_makes_no_process_call(self):
        n = self.make(platform="linux")
        n("BRIDGE-1", "Titel")
        self.runner.assert_not_called()

    def test_windows_call_shape(self):
        n = self.make()
        title = "Titel'; Remove-Item -Recurse C:\\ #\"$(evil)"
        n("BRIDGE-0069", title)
        self.runner.assert_called_once()
        args, kwargs = self.runner.call_args
        argv = args[0]
        self.assertIsInstance(argv, list)
        self.assertEqual(argv[:3], ["powershell.exe", "-NoProfile", "-NonInteractive"])
        self.assertFalse(kwargs.get("shell"))
        self.assertEqual(kwargs["timeout"], 7)
        # Texte nur in Umgebungsvariablen, nie im Befehlsstring
        self.assertEqual(kwargs["env"]["ACB_NOTIFY_ID"], "BRIDGE-0069")
        self.assertEqual(kwargs["env"]["ACB_NOTIFY_TITLE"], title)
        self.assertEqual(kwargs["env"]["X"], "1")
        joined = " ".join(argv)
        self.assertNotIn("BRIDGE-0069", joined)
        self.assertNotIn("evil", joined)

    def test_long_text_is_truncated(self):
        n = self.make()
        n("BRIDGE-1", "x" * 5000)
        self.assertLessEqual(len(self.runner.call_args.kwargs["env"]["ACB_NOTIFY_TITLE"]), 200)

    def test_missing_powershell_is_fail_open(self):
        n = self.make(runner=mock.Mock(side_effect=FileNotFoundError("powershell.exe")))
        err = StringIO()
        with redirect_stderr(err):
            n("BRIDGE-1", "t")
        self.assertIn("fehlgeschlagen", err.getvalue())

    def test_timeout_is_fail_open(self):
        import subprocess
        n = self.make(runner=mock.Mock(side_effect=subprocess.TimeoutExpired("powershell.exe", 7)))
        with redirect_stderr(StringIO()) as err:
            n("BRIDGE-1", "t")
        self.assertIn("fehlgeschlagen", err.getvalue())

    def test_nonzero_exit_code_is_logged_only(self):
        n = self.make(runner=mock.Mock(return_value=mock.Mock(returncode=1)))
        with redirect_stderr(StringIO()) as err:
            n("BRIDGE-1", "t")
        self.assertIn("Exit-Code 1", err.getvalue())


def _task_doc(task_id, status, title="Titel"):
    return {
        "schema_version": "1.0", "kind": "bridge_task", "bridge_task_id": task_id,
        "project_id": "p", "title": title, "description": "d", "task_class": "FEATURE",
        "repository": "r", "branch": "main", "permissions": ["READ_ONLY"],
        "status": status, "created_at": "2026-01-01T00:00:00Z", "created_by": "x",
    }


def _tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(root)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


class HookIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="acb-notify-"))
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        for name in ("tasks", "results", "audit"):
            (self.tmp / name).mkdir()
        self.store = Store(root=self.tmp, schema_dir=SCHEMA_DIR)

    def put(self, task_id, status, title="Titel"):
        d = self.tmp / "tasks" / task_id
        d.mkdir(exist_ok=True)
        (d / "task.yaml").write_text(
            yaml.safe_dump(_task_doc(task_id, status, title)), encoding="utf-8")

    def test_hook_detects_via_store_and_writes_nothing(self):
        calls = []
        self.put("BRIDGE-0001", WAITING, "Altbestand")
        self.put("BRIDGE-0002", "RUNNING")
        hook = cli_mod._build_notify_hook(self.store, lambda t, ti: calls.append((t, ti)))
        before = _tree_digest(self.tmp)
        hook()
        self.assertEqual(calls, [])  # Altbestand still
        self.put("BRIDGE-0002", WAITING, "Fertig")
        mid = _tree_digest(self.tmp)
        hook()
        hook()
        self.assertEqual(calls, [("BRIDGE-0002", "Fertig")])
        self.assertEqual(_tree_digest(self.tmp), mid)  # Hook aendert nichts
        self.assertNotEqual(before, mid)
        self.assertFalse((self.tmp / "audit" / "audit.jsonl").exists())


class PullLoopHookTests(unittest.TestCase):
    RESULT = {"pulled": True, "updated": False, "stdout": "", "stderr": "", "error": None}

    def run_loop(self, after_pull, min_calls=2):
        stop, lock, n = threading.Event(), threading.Lock(), []

        def hook():
            n.append(1)
            after_pull()

        with mock.patch.object(cli_mod.gitops, "git_pull", return_value=self.RESULT), \
                redirect_stderr(StringIO()) as err:
            t = threading.Thread(target=cli_mod._pull_loop,
                                 args=("/x", 0.01, stop, lock, hook))
            t.start()
            for _ in range(400):
                if len(n) >= min_calls:
                    break
                stop.wait(0.005)
            alive_during = t.is_alive()
            stop.set()
            t.join(timeout=5)
        return len(n), alive_during, t.is_alive(), err.getvalue()

    def test_after_pull_called_and_thread_survives_exception(self):
        def boom():
            raise RuntimeError("hook kaputt")

        calls, alive, alive_after, err = self.run_loop(boom)
        self.assertGreaterEqual(calls, 2)
        self.assertTrue(alive)
        self.assertFalse(alive_after)
        self.assertIn("hook kaputt", err)

    def test_default_none_unchanged(self):
        stop, lock = threading.Event(), threading.Lock()
        with mock.patch.object(cli_mod.gitops, "git_pull", return_value=self.RESULT), \
                redirect_stderr(StringIO()):
            t = threading.Thread(target=cli_mod._pull_loop, args=("/x", 0.01, stop, lock))
            t.start()
            stop.wait(0.05)
            stop.set()
            t.join(timeout=5)
        self.assertFalse(t.is_alive())


class WebUiNotifyFlagTests(unittest.TestCase):
    def serve(self, *extra):
        class Fake:
            server_address = ("127.0.0.1", 8420)
            git_lock = threading.Lock()

            def serve_forever(self):
                raise KeyboardInterrupt

            def server_close(self):
                pass

        tmp = tempfile.mkdtemp(prefix="acb-notify-")
        self.addCleanup(__import__("shutil").rmtree, tmp, True)
        out, err = StringIO(), StringIO()
        with mock.patch("bridge.webui.serve", return_value=Fake()), \
                mock.patch.object(cli_mod, "_maybe_start_pull_thread",
                                  return_value=(threading.Event(), None)) as start, \
                mock.patch.object(cli_mod, "_build_notify_hook",
                                  return_value=lambda: None) as build, \
                redirect_stdout(out), redirect_stderr(err):
            code = cli_mod.main(["--root", tmp, "--schema-dir", str(SCHEMA_DIR),
                                 "webui", "serve", "--actor", "x", *extra])
        return code, out.getvalue(), start, build

    def test_without_notify_unchanged(self):
        code, out, start, build = self.serve("--pull-interval", "5")
        self.assertEqual(code, 0)
        build.assert_not_called()
        self.assertIsNone(start.call_args.args[3])
        self.assertNotIn("Benachrichtigung", out)

    def test_with_notify_passes_hook(self):
        code, out, start, build = self.serve("--pull-interval", "5", "--notify")
        self.assertEqual(code, 0)
        build.assert_called_once()
        self.assertIsNotNone(start.call_args.args[3])

    def test_notify_with_interval_zero_prints_hint_no_error(self):
        code, out, start, build = self.serve("--pull-interval", "0", "--notify")
        self.assertEqual(code, 0)
        build.assert_not_called()
        self.assertIn("--notify braucht", out)


if __name__ == "__main__":
    unittest.main()
