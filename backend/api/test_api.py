from __future__ import annotations
import sqlite3
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))

from main import init_database, query_matches, query_news
from socials import DEFAULT_SOCIALS, format_followers


class ApiDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        init_database(self.db_path)
        self.connection = sqlite3.connect(self.db_path)

    def tearDown(self) -> None:
        self.connection.close()
        self.temp_dir.cleanup()

    def test_serializes_news_with_frontend_field_names(self) -> None:
        self.connection.execute(
            "INSERT INTO news (titre, image, description) VALUES (?, ?, ?)",
            ("Tournoi gagné", "img/tournoi.png", "Victoire en finale"),
        )
        self.connection.commit()

        news = query_news(self.connection)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]["img"], "img/tournoi.png")
        self.assertEqual(news[0]["desc"], "Victoire en finale")
        self.assertNotIn("image", news[0])

    def test_serializes_match_with_frontend_field_names_and_team_join(self) -> None:
        self.connection.execute(
            "INSERT INTO teams (nom, abreviation, logo) VALUES (?, ?, ?)",
            ("LowSens", "SEN", "logo-sen.png"),
        )
        self.connection.execute(
            "INSERT INTO teams (nom, abreviation, logo) VALUES (?, ?, ?)",
            ("Team B", "TMB", "logo-b.png"),
        )
        self.connection.execute(
            "INSERT INTO matches (team_a, team_b, date_heure, jeu, score) VALUES (?, ?, ?, ?, ?)",
            ("sen", "TMB", "22/09 21h", "Valorant", "-"),
        )
        self.connection.commit()

        matches = query_matches(self.connection)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["teamA"], "logo-sen.png")
        self.assertEqual(matches[0]["teamAName"], "LowSens")
        self.assertEqual(matches[0]["teamB"], "logo-b.png")
        self.assertEqual(matches[0]["teamBName"], "Team B")
        self.assertEqual(matches[0]["date"], "22/09 21h")
        self.assertEqual(matches[0]["jeu"], "Valorant")

    def test_format_followers(self) -> None:
        self.assertEqual(format_followers(12_000, "abonnés"), "12 k abonnés")
        self.assertEqual(format_followers(2_243, "abonnés"), "2,2 k abonnés")
        self.assertEqual(format_followers(325, "membres"), "325 membres")
        self.assertEqual(format_followers(1_500_000, "abonnés"), "1,5 M abonnés")

    def test_default_socials_structure(self) -> None:
        for platform in ("instagram", "twitch", "youtube", "twitter", "tiktok", "discord"):
            self.assertIn(platform, DEFAULT_SOCIALS)
            self.assertIn("formatted", DEFAULT_SOCIALS[platform])


if __name__ == "__main__":
    unittest.main()

