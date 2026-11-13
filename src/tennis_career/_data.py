"""Name lookup, career data retrieval, and match cleaning."""

import csv
import json
import re
import unicodedata
from functools import lru_cache
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

import pandas as pd

_PLAYER_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_{tour}/master/{tour}_players.csv"
_CAREER_URL = "https://www.tennisabstract.com/jsmatches/{slug}Career.js"
_DAYS_PER_YEAR = 365.2425


def _download(url):
    with urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8-sig", errors="replace")


def _name_key(name):
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_name.casefold())


@lru_cache(maxsize=2)
def _player_index(tour):
    records = csv.DictReader(StringIO(_download(_PLAYER_URL.format(tour=tour))))
    index = {}
    for row in records:
        name = f"{row['name_first']} {row['name_last']}".strip()
        if re.fullmatch(r"\d{8}", row["dob"] or ""):
            index.setdefault(_name_key(name), set()).add((name, row["dob"]))
    return index


def _resolve_player(name):
    key = _name_key(name) if isinstance(name, str) else ""
    if not key:
        raise ValueError("Enter a player's full name, such as 'Serena Williams'.")
    matches = _player_index("wta").get(key, set()) | _player_index("atp").get(key, set())
    if not matches:
        raise ValueError(f"Player {name!r} was not found. Check the spelling and use their full name.")
    if len(matches) > 1:
        raise ValueError(f"Player name {name!r} matches multiple records.")
    return next(iter(matches))


def _career_script(name):
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = quote(re.sub(r"[^A-Za-z0-9]", "", ascii_name))
    try:
        return _download(_CAREER_URL.format(slug=slug))
    except HTTPError as error:
        if error.code == 404:
            raise ValueError(f"Tennis Abstract has no career file for {name!r}.") from error
        raise


def _parse_matches(script):
    assignment = re.search(r"\bmorematchmx\s*=\s*(?=\[)", script)
    if assignment is None:
        raise ValueError("The Tennis Abstract career file is missing its match array.")
    try:
        rows, _ = json.JSONDecoder().raw_decode(script[assignment.end():])
    except json.JSONDecodeError as error:
        raise ValueError("Could not parse the Tennis Abstract match array.") from error
    return [row for row in rows if isinstance(row, list) and len(row) >= 17]


def _opponent_ages(raw, match_dates):
    birth_date = raw.str.fullmatch(r"\d{8}", na=False)
    dates = pd.to_datetime(raw.where(birth_date), format="%Y%m%d", errors="coerce")
    ages_from_dates = (match_dates - dates).dt.days / _DAYS_PER_YEAR
    ages_from_numbers = pd.to_numeric(raw.where(~birth_date), errors="coerce")
    return ages_from_dates.where(birth_date, ages_from_numbers)


def _clean_matches(rows, name, birth_date):
    records = [(row[0], row[1], row[4], row[11], row[16]) for row in rows]
    matches = pd.DataFrame(records, columns=["match_date", "tournament", "result",
                                             "opponent", "opponent_age"])
    matches["match_date"] = pd.to_datetime(matches["match_date"], format="%Y%m%d", errors="coerce")
    matches["player"] = name
    matches["player_age"] = (matches["match_date"] - pd.to_datetime(birth_date, format="%Y%m%d")).dt.days
    matches["player_age"] /= _DAYS_PER_YEAR
    matches["opponent_age"] = _opponent_ages(matches["opponent_age"].astype("string"),
                                             matches["match_date"])
    matches = matches.loc[matches["result"].isin(["W", "L"]) &
                          matches["player_age"].between(0, 120) &
                          matches["opponent_age"].between(0, 120)].copy()
    matches["age_difference"] = matches["player_age"] - matches["opponent_age"]
    return matches.sort_values("match_date", kind="stable", ignore_index=True)


def get_career_matches(player_name: str) -> pd.DataFrame:
    """Return plottable career matches with both ages in decimal years."""
    try:
        name, birth_date = _resolve_player(player_name)
        rows = _parse_matches(_career_script(name))
    except (URLError, TimeoutError) as error:
        raise ConnectionError("Could not download player data. Check your connection and try again.") from error
    matches = _clean_matches(rows, name, birth_date)
    if matches.empty:
        raise ValueError(f"No matches with usable ages and results were found for {name!r}.")
    return matches
