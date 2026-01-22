#!/usr/bin/env python3
"""
generate_commit_days.py

Generates `commit-activity.svg` for the profile README.
"""
import os
import sys
import math
import requests
from datetime import datetime, timezone, date

# Configuration
USERNAME = "kkusima"
YEAR = datetime.now(timezone.utc).year  # auto-updates each year; change to 2026 if you want to lock it
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OUTFILE = "commit-activity.svg"

if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable not found. The script needs a token to call the GitHub GraphQL API.")
    print("If running in GitHub Actions you can set env: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}")
    sys.exit(1)


def fetch_contribution_days(username, year, token):
    """
    Fetch contributionDays for the given year. Count only days up to today (UTC)
    to avoid counting future-dated days or timezone mismatches.
    """
    # GraphQL query returns contributionCalendar.weeks[].contributionDays[] with date strings like "2026-01-22"
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
            totalContributions
          }
        }
      }
    }
    """

    # Use UTC "today" so API range and our counting use the same reference
    now_utc = datetime.now(timezone.utc)
    today_utc_date = now_utc.date()

    if year == now_utc.year:
        to_iso = now_utc.strftime("%Y-%m-%dT23:59:59Z")
    else:
        # whole year
        to_iso = f"{year}-12-31T23:59:59Z"

    variables = {
        "username": username,
        "from": f"{year}-01-01T00:00:00Z",
        "to": to_iso
    }

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    resp = requests.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    resp.raise_for_status()
    payload = resp.json()

    if "errors" in payload:
        raise RuntimeError("GraphQL errors: {}".format(payload["errors"]))

    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

    days_with_commits = 0
    total_contributions = 0

    # Count only days up to today_utc_date (ignore any future dates that might appear)
    for week in weeks:
        for day in week["contributionDays"]:
            day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if day_date > today_utc_date:
                # Skip future-dated days (defensive)
                continue
            c = day.get("contributionCount", 0)
            if c > 0:
                days_with_commits += 1
            total_contributions += c

    return days_with_commits, total_contributions


def calculate_days_elapsed(year):
    """
    Calculate how many days have elapsed in `year`, using UTC date for consistency
    with GitHub contribution dates.
    """
    today = datetime.now(timezone.utc).date()

    if today.year == year:
        start_of_year = date(year, 1, 1)
        return (today - start_of_year).days + 1
    elif today.year > year:
        # full year
        return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
    else:
        return 0

# (rest of file unchanged)
