import sqlite3
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))

import bot


class BotDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.connection = sqlite3.connect(Path(self.temp_dir.name) / "test.db")
        self.connection.execute(
            "CREATE TABLE teams (id INTEGER PRIMARY KEY, nom TEXT UNIQUE, abreviation TEXT UNIQUE, logo TEXT)"
        )
        self.connection.execute(
            "CREATE TABLE matches (id INTEGER PRIMARY KEY, team_a TEXT, team_b TEXT, date_heure TEXT, jeu TEXT, score TEXT)"
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()
        self.temp_dir.cleanup()

    def test_normalize_abbreviation(self) -> None:
        self.assertEqual(bot.normalize_abreviation("  sen  "), "SEN")

    def test_team_exists_is_case_insensitive(self) -> None:
        self.connection.execute(
            "INSERT INTO teams (nom, abreviation, logo) VALUES (?, ?, ?)",
            ("Team Sens", "SEN", "logo.png"),
        )
        self.connection.commit()

        self.assertTrue(bot.team_exists(self.connection.cursor(), "sen"))
        self.assertFalse(bot.team_exists(self.connection.cursor(), "XYZ"))

    def test_insert_and_fetch_match(self) -> None:
        cursor = self.connection.cursor()
        bot.insert_match(cursor, "SEN", "ABC", "22/09", "21h")
        self.connection.commit()

        matches = bot.fetch_all_matches(cursor)

        self.assertEqual(matches, [(1, "SEN", "ABC", "22/09 21h", None, "-", "Inconnu")])

    def test_unknown_schema_raises_error(self) -> None:
        connection = sqlite3.connect(":memory:")
        with self.assertRaisesRegex(RuntimeError, "Schéma"):
            bot.insert_match(connection.cursor(), "SEN", "ABC", "22/09", "21h")
        connection.close()


if __name__ == "__main__":
    unittest.main()
