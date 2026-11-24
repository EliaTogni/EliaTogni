import os
import tempfile
import unittest
from unittest import mock

from city.__main__ import main
from city.data import CalendarError, Day


class MainTest(unittest.TestCase):
    def test_missing_token_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as out, mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(main(["--login", "x", "--out-dir", out]), 1)
            self.assertEqual(os.listdir(out), [])

    def test_api_error_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as out, \
             mock.patch.dict(os.environ, {"GITHUB_TOKEN": "t"}), \
             mock.patch("city.__main__.fetch_days", side_effect=CalendarError("boom")):
            self.assertEqual(main(["--login", "x", "--out-dir", out]), 1)
            self.assertEqual(os.listdir(out), [])

    def test_writes_both_themes(self):
        with tempfile.TemporaryDirectory() as out, \
             mock.patch.dict(os.environ, {"GITHUB_TOKEN": "t"}), \
             mock.patch("city.__main__.fetch_days", return_value=[Day(0, 0, 3, "2025-11-23")]):
            self.assertEqual(main(["--login", "x", "--out-dir", out]), 0)
            self.assertEqual(sorted(os.listdir(out)), ["city-dark.svg", "city-light.svg"])


if __name__ == "__main__":
    unittest.main()
