#!/usr/bin/env python3
import os
import sys
import requests
import math
from datetime import datetime

# Use the current year by default; change to 2026 if you want a fixed-year output
YEAR = datetime.now().year
USERNAME = "kkusima"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN environment variable not found. The script needs a token to call the GitHub GraphQL API.")
    print("If running in GitHub Actions you can set env: GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}")
    sys.exit(1)


def fetch_contribution_days(username, year, token):
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "username": username,
        "from": f"{year}-01-01T00:00:00Z",
        "to": f"{year}-12-31T23:59:59Z"
    }

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    resp = requests.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    resp.raise_for_status()
    payload = resp.json()

    # Basic error handling for GraphQL payload
    if "errors" in payload:
        raise RuntimeError("GraphQL errors: {}".format(payload["errors"]))

    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

    days_with_commits = 0
    total_contributions = 0

    for week in weeks:
        for day in week["contributionDays"]:
            c = day.get("contributionCount", 0)
            if c > 0:
                days_with_commits += 1
            total_contributions += c

    return days_with_commits, total_contributions


def calculate_days_elapsed(year):
    today = datetime.now()
    if today.year == year:
        start_of_year = datetime(year, 1, 1)
        return (today - start_of_year).days + 1
    elif today.year > year:
        # full year
        return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
    else:
        return 0


def generate_svg(days_with_commits, total_contributions, days_elapsed, year):
    percentage = (days_with_commits / days_elapsed * 100) if days_elapsed > 0 else 0.0

    if percentage >= 80:
        ring_color = "#40c463"
    elif percentage >= 60:
        ring_color = "#9be9a8"
    elif percentage >= 40:
        ring_color = "#ffd33d"
    else:
        ring_color = "#f97583"

    r = 54.0
    circumference = 2.0 * math.pi * r
    progress_length = (percentage / 100.0) * circumference

    progress_str = "{:.1f}".format(progress_length)
    circ_str = "{:.1f}".format(circumference)
    pct_str = "{:.0f}".format(percentage)
    contrib_str = "{:,}".format(total_contributions)

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="160" viewBox="0 0 400 160">\n'
        '  <defs>\n'
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">\n'
        '      <stop offset="0%" style="stop-color:#0d1117;stop-opacity:1" />\n'
        '      <stop offset="100%" style="stop-color:#161b22;stop-opacity:1" />\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="400" height="160" rx="12" fill="url(#bgGrad)" stroke="#30363d" stroke-width="1"/>\n'
        '  <g transform="translate(80, 80)">\n'
        '    <circle cx="0" cy="0" r="54" fill="none" stroke="#21262d" stroke-width="8"/>\n'
        f'    <circle cx="0" cy="0" r="54" fill="none" stroke="{ring_color}" stroke-width="8"\n'
        f'            stroke-dasharray="{progress_str} {circ_str}"\n'
        '            stroke-linecap="round" transform="rotate(-90)"/>\n'
        f'    <text x="0" y="-8" text-anchor="middle" fill="#ffffff" font-family="Segoe UI, sans-serif" font-size="28" font-weight="bold">{days_with_commits}</text>\n'
        '    <text x="0" y="14" text-anchor="middle" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="11">days</text>\n'
        '  </g>\n'
        '  <g transform="translate(170, 45)">\n'
        f'    <text x="0" y="0" fill="#58a6ff" font-family="Segoe UI, sans-serif" font-size="14" font-weight="600">📅 {year} Commit Activity</text>\n'
        '    <text x="0" y="32" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="12">Days with commits</text>\n'
        f'    <text x="0" y="50" fill="#ffffff" font-family="Segoe UI, sans-serif" font-size="16" font-weight="500">{days_with_commits} / {days_elapsed}</text>\n'
        '    <text x="0" y="78" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="12">Total contributions</text>\n'
        f'    <text x="0" y="96" fill="#ffffff" font-family="Segoe UI, sans-serif" font-size="16" font-weight="500">{contrib_str}</text>\n'
        '  </g>\n'
        '  <g transform="translate(320, 138)">\n'
        f'    <text x="0" y="0" text-anchor="end" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="12">{pct_str}% consistency</text>\n'
        '  </g>\n'
        '</svg>\n'
    )

    return svg


def main():
    days_with_commits, total_contributions = fetch_contribution_days(USERNAME, YEAR, GITHUB_TOKEN)
    days_elapsed = calculate_days_elapsed(YEAR)
    svg_content = generate_svg(days_with_commits, total_contributions, days_elapsed, YEAR)

    with open("commit-activity.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("✅ Generated commit-activity.svg")
    print("Days with commits: {}/{}".format(days_with_commits, days_elapsed))
    print("Total contributions: {}".format(total_contributions))


if __name__ == "__main__":
    main()
