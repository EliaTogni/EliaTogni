"""Reads a user's contribution calendar from the GitHub GraphQL API."""
import json
import urllib.error
import urllib.request
from datetime import date
from typing import NamedTuple

API_URL = "https://api.github.com/graphql"
QUERY = (
    "query($login:String!){user(login:$login){contributionsCollection{"
    "contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"
)


class Day(NamedTuple):
    week: int
    weekday: int  # 0 = Sunday
    count: int
    date: str


class CalendarError(Exception):
    pass


def parse_response(payload: dict) -> list[Day]:
    if payload.get("errors"):
        raise CalendarError("; ".join(e.get("message", "unknown error") for e in payload["errors"]))
    user = (payload.get("data") or {}).get("user")
    if not user:
        raise CalendarError("user not found")
    try:
        weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    except (KeyError, TypeError) as e:
        raise CalendarError(f"missing contribution calendar: {e}") from e
    return [
        Day(w, (date.fromisoformat(d["date"]).weekday() + 1) % 7, d["contributionCount"], d["date"])
        for w, week in enumerate(weeks)
        for d in week["contributionDays"]
    ]


def fetch_days(login: str, token: str) -> list[Day]:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.URLError as e:  # HTTPError is a subclass
        raise CalendarError(str(e)) from e
    return parse_response(payload)
