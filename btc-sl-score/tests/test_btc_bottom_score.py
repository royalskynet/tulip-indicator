import io
import sqlite3
import tempfile
import unittest
from contextlib import ExitStack, closing, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import btc_bottom_score as btc


class ScoreTests(unittest.TestCase):
    def signals(self, values):
        stack = ExitStack()
        for name, value in zip(("fear_greed", "mvrv_zscore", "hash_ribbon_depth",
                                "price_ma200_ratio", "sth_mvrv", "lth_sopr", "nupl"), values):
            stack.enter_context(patch.object(btc, name, return_value=value))
        return stack

    def test_arguments(self):
        args = btc.parse_args([])
        self.assertFalse(args.summary)
        self.assertFalse(args.selftest)
        self.assertIsNone(args.history)
        self.assertTrue(btc.parse_args(["--summary"]).summary)
        self.assertTrue(btc.parse_args(["--selftest"]).selftest)
        self.assertEqual(btc.parse_args(["--history"]).history, 30)
        self.assertEqual(btc.parse_args(["--history", "7"]).history, 7)
        for value in ("0", "-1", "1.5", "abc"):
            with self.subTest(value=value), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    btc.parse_args(["--history", value])
                self.assertEqual(error.exception.code, 2)

    def test_history_dispatch(self):
        with patch.object(btc, "print_history") as history, patch.object(btc, "collect") as collect:
            self.assertEqual(btc.main(["--history", "5"]), 0)
            history.assert_called_once_with(5)
            collect.assert_not_called()

    def test_selftest_offline(self):
        with patch.object(btc, "collect") as collect, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(btc.main(["--selftest"]), 0)
            self.assertEqual(out.getvalue(), "selftest OK\n")
            collect.assert_not_called()

    def test_partial_data_renormalized(self):
        with self.signals([20, 1, None, 0.8, None, None, None]), redirect_stderr(io.StringIO()) as err:
            rows, score, _, coverage = btc.collect()
        self.assertAlmostEqual(coverage, 0.45)
        expected = sum(s * w for _, s, _, w in rows if s is not None) / 0.45
        self.assertAlmostEqual(score, expected)
        self.assertIn("Hash Ribbon signal unavailable", err.getvalue())

    def test_refuses_insufficient_signals(self):
        for values in ([None] * 7, [20, 1, None, None, None, None, None]):
            with self.subTest(values=values), self.signals(values), patch.object(btc, "save_history") as save:
                with redirect_stderr(io.StringIO()) as err, redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(btc.main([]), 2)
                self.assertIn("refusing to score", err.getvalue())
                self.assertEqual(out.getvalue(), "")
                save.assert_not_called()

    def test_table_and_summary(self):
        for argv, expected in (([], "DATA COVERAGE"), (["--summary"], "BCI")):
            with self.subTest(argv=argv), self.signals([20, 1, -0.1, 0.8, 0.9, 1, 0.2]):
                with patch.object(btc, "save_history"), redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(btc.main(argv), 0)
                self.assertIn(expected, out.getvalue())

    def test_retry_diagnostic_and_success(self):
        with patch.object(btc.urllib.request, "urlopen", side_effect=OSError("provider offline")), \
                patch.object(btc.time, "sleep") as sleep, redirect_stderr(io.StringIO()) as err:
            self.assertIsNone(btc._get("https://example.com", retries=2))
            sleep.assert_called_once()
            self.assertIn("provider offline", err.getvalue())
        with patch.object(btc.urllib.request, "urlopen") as request, redirect_stderr(io.StringIO()) as err:
            request.return_value.__enter__.return_value.read.return_value = b'{"ok": true}'
            self.assertEqual(btc._get("https://example.com"), {"ok": True})
            self.assertEqual(err.getvalue(), "")

    def test_history_roundtrip_and_close(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(btc, "DB_PATH", Path(directory) / "history.db"):
            with redirect_stdout(io.StringIO()) as out:
                btc.print_history(3)
            self.assertIn("no history yet", out.getvalue())
            connections = []
            original = btc._conn

            def connect():
                connection = original()
                connections.append(connection)
                return connection

            with patch.object(btc, "_conn", side_effect=connect):
                btc.save_history({"fng": 20}, 77.5, 0.1)
                with redirect_stdout(io.StringIO()) as out:
                    btc.print_history(3)
            self.assertIn("77.5", out.getvalue())
            self.assertIn("20", out.getvalue())
            for connection in connections:
                with self.assertRaises(sqlite3.ProgrammingError):
                    connection.execute("SELECT 1")
            with closing(sqlite3.connect(btc.DB_PATH)) as connection:
                self.assertEqual(connection.execute("SELECT composite, fng FROM sl_score").fetchone(), (77.5, 20))


if __name__ == "__main__":
    unittest.main()
