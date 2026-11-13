"""Name lookup, career data retrieval, and match cleaning."""

import json
import re
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

_PROFILE_URL = "https://www.tennisabstract.com/cgi-bin/{page}.cgi?{query}"
_CAREER_URL = "https://www.tennisabstract.com/jsmatches/{slug}Career.js"
_DAYS_PER_YEAR = 365.2425


def _download(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig", errors="replace")


def _player_slug(name):
    if not isinstance(name, str):
        return ""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    words = re.findall(r"[A-Za-z0-9]+", ascii_name)
    return "".join(word[0].upper() + (word[1:].lower() if word.isupper() else word[1:])
                   for word in words)


def _profile_birth_date(page, slug):
    try:
        profile = _download(_PROFILE_URL.format(page=page, query=urlencode({"p": slug})))
    except HTTPError as error:
        if error.code == 404:
            return None
        raise
    match = re.search(r"(?m)^\s*var dob\s*=\s*['\"]?(\d{8})\b", profile)
    return match[1] if match else None


def _resolve_player(name):
    slug = _player_slug(name)
    if not slug:
        raise ValueError("Enter a player's full name, such as 'Serena Williams'.")
    for page in ("player", "wplayer"):
        birth_date = _profile_birth_date(page, slug)
        if birth_date:
            display_name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", slug)
            return slug, display_name, birth_date
    raise ValueError(f"Player {name!r} was not found. Check the spelling and use their full name.")


def _career_script(slug):
    try:
        return _download(_CAREER_URL.format(slug=slug))
    except HTTPError as error:
        if error.code == 404:
            raise ValueError(f"Tennis Abstract has no career file for {slug!r}.") from error
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


def _match_frame(rows, name):
    records = [(row[0], row[1], row[4], row[11], row[16]) for row in rows]
    matches = pd.DataFrame(records, columns=["match_date", "tournament", "result",
                                             "opponent", "opponent_age"])
    matches["match_date"] = pd.to_datetime(matches["match_date"], format="%Y%m%d", errors="coerce")
    matches["player"] = name
    return matches


def _clean_matches(rows, name, birth_date):
    matches = _match_frame(rows, name)
    player_birth_date = pd.to_datetime(birth_date, format="%Y%m%d")
    matches["player_age"] = (matches["match_date"] - player_birth_date).dt.days / _DAYS_PER_YEAR
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
        slug, name, birth_date = _resolve_player(player_name)
        rows = _parse_matches(_career_script(slug))
    except (URLError, TimeoutError) as error:
        raise ConnectionError("Could not download player data. Check your connection and try again.") from error
    matches = _clean_matches(rows, name, birth_date)
    if matches.empty:
        raise ValueError(f"No matches with usable ages and results were found for {name!r}.")
    return matches
