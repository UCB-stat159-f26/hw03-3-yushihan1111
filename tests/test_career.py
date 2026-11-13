"""Offline tests using shortened copies of the assignment's career fixtures."""

from datetime import date
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

from tennis_career import get_career_matches, plot_career_matches
from tennis_career import _data

_FIXTURES = Path(__file__).with_name("fixtures")


def _offline_download(url):
    filename = url.rsplit("/", 1)[-1]
    profiles = {
        "wplayer.cgi?p=SerenaWilliams": "var dob = 19810926;",
        "player.cgi?p=RafaelNadal": "var dob = 19860603;",
    }
    if ".cgi?" in filename:
        return profiles.get(filename, "")
    return (_FIXTURES / filename).read_text(encoding="utf-8")


class CareerTests(TestCase):
    def setUp(self):
        self.addCleanup(plt.close, "all")
        mock = patch.object(_data, "_download", side_effect=_offline_download)
        mock.start()
        self.addCleanup(mock.stop)

    def test_womens_match_ages_and_name_variants(self):
        for name in ("serena williams", "Serena Williams", "SerenaWilliams"):
            with self.subTest(name=name):
                matches = get_career_matches(name)
                self.assertEqual(len(matches), 3)
                first = matches.iloc[0]
                self.assertEqual(first["result"], "L")
                days = (date(1981, 9, 26) - date(1977, 1, 19)).days
                self.assertAlmostEqual(first["age_difference"], -days / 365.2425)

    def test_mens_numeric_age_and_plot_coordinates(self):
        matches = get_career_matches("Rafael Nadal")
        self.assertEqual(list(matches["result"]), ["L", "L", "W"])
        self.assertAlmostEqual(matches.iloc[0]["opponent_age"], 22.264202601)
        axes = plot_career_matches(matches)
        self.assertEqual([len(group.get_offsets()) for group in axes.collections], [1, 2])
        winner = matches.iloc[2]
        x, y = axes.collections[0].get_offsets()[0]
        self.assertAlmostEqual(x, winner["player_age"])
        self.assertAlmostEqual(y, winner["age_difference"])

    def test_unknown_player(self):
        with self.assertRaisesRegex(ValueError, "GastonSanchez.*not found"):
            get_career_matches("GastonSanchez")

    def test_missing_ages_are_removed(self):
        rows = _data._parse_matches(_offline_download("SerenaWilliamsCareer.js"))
        rows[0][16] = ""
        rows[1][16] = "19700230"
        self.assertEqual(len(_data._clean_matches(rows, "Serena Williams", "19810926")), 1)

    def test_missing_or_malformed_match_array(self):
        for script in ("var unrelated = [];", "var morematchmx = [[;"):
            with self.subTest(script=script), self.assertRaisesRegex(ValueError, "match array"):
                _data._parse_matches(script)
