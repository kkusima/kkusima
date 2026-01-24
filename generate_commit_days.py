#!/usr/bin/env python3
"""
generate_commit_days.py

Generates a premium `commit-activity.svg` for the profile README.
Uses GitHub GraphQL API to fetch contribution data for the current year.
Strictly follows the visual representation of the contribution graph.
"""
import os
import sys
import requests
from datetime import datetime, timezone, date

# Configuration
USERNAME = "kkusima"
YEAR = datetime.now(timezone.utc).year  # Dynamic year
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OUTFILE = "commit-activity.svg"

def fetch_contribution_days(username, year, token):
    """
    Fetch contributionDays for the given year. 
    Strictly follows the visual contribution graph by checking 'contributionLevel'.
    """
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                contributionLevel
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
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    resp.raise_for_status()
    payload = resp.json()

    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")

    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    
    today_utc = datetime.now(timezone.utc).date()
    days_with_activity = 0
    total_contributions = 0

    for week in weeks:
        for day in week["contributionDays"]:
            day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if day_date > today_utc:
                continue
                
            # Contribution level 'NONE' means an empty (grey) square on the graph
            level = day.get("contributionLevel", "NONE")
            if level != "NONE":
                days_with_activity += 1
            
            total_contributions += day.get("contributionCount", 0)

    return days_with_activity, total_contributions

def calculate_days_elapsed(year):
    """
    Calculate how many days have elapsed in the given year up to today (UTC).
    """
    today = datetime.now(timezone.utc).date()
    if today.year == year:
        start_of_year = date(year, 1, 1)
        return (today - start_of_year).days + 1
    elif today.year > year:
        # Full year
        return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
    else:
        return 0

def generate_svg(days_with_activity, total_contributions, days_elapsed, year):
    """
    Generate a premium, modern SVG with a progress ring and stats.
    """
    consistency = (days_with_activity / days_elapsed * 100) if days_elapsed > 0 else 0
    
    # Elegant color palette
    if consistency >= 85:
        accent_color = "#3fb950"  # GitHub Green
    elif consistency >= 60:
        accent_color = "#d29922"  # GitHub Gold/Yellow
    else:
        accent_color = "#f85149"  # GitHub Red

    # Progress Ring Math
    radius = 54
    circumference = 2 * 3.14159 * radius
    progress = (consistency / 100) * circumference
    
    last_updated = datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="450" height="180" viewBox="0 0 450 180">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d1117;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#161b22;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
      <feOffset dx="0" dy="2" result="offsetblur" />
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.5" />
      </feComponentTransfer>
      <feMerge>
        <feMergeNode />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Main Card -->
  <rect width="450" height="180" rx="16" fill="url(#bgGrad)" stroke="#30363d" stroke-width="1.5"/>

  <!-- Progress Circle Section -->
  <g transform="translate(90, 90)">
    <!-- Background Circle -->
    <circle cx="0" cy="0" r="{radius}" fill="none" stroke="#21262d" stroke-width="10"/>
    <!-- Progress Circle -->
    <circle cx="0" cy="0" r="{radius}" fill="none" stroke="{accent_color}" stroke-width="10"
            stroke-dasharray="{progress:.1f} {circumference:.1f}"
            stroke-linecap="round" transform="rotate(-90)"
            style="transition: stroke-dasharray 0.5s ease;"/>
    
    <!-- Central Text -->
    <text x="0" y="-5" text-anchor="middle" fill="#ffffff" font-family="Segoe UI, -apple-system, sans-serif" font-size="32" font-weight="800" filter="url(#shadow)">{int(consistency)}%</text>
    <text x="0" y="18" text-anchor="middle" fill="#8b949e" font-family="Segoe UI, -apple-system, sans-serif" font-size="12" font-weight="500">CONSISTENCY</text>
  </g>

  <!-- Statistics Section -->
  <g transform="translate(200, 45)">
    <text x="0" y="0" fill="#58a6ff" font-family="Segoe UI, -apple-system, sans-serif" font-size="16" font-weight="700">📅 {year} Activity Streak</text>
    
    <g transform="translate(0, 35)">
      <text x="0" y="0" fill="#8b949e" font-family="Segoe UI, -apple-system, sans-serif" font-size="13">Active Days (Visual)</text>
      <text x="0" y="22" fill="#ffffff" font-family="Segoe UI, -apple-system, sans-serif" font-size="18" font-weight="600">{days_with_activity} / {days_elapsed}</text>
    </g>
    
    <g transform="translate(0, 80)">
      <text x="0" y="0" fill="#8b949e" font-family="Segoe UI, -apple-system, sans-serif" font-size="13">Total Contributions</text>
      <text x="0" y="22" fill="#ffffff" font-family="Segoe UI, -apple-system, sans-serif" font-size="18" font-weight="600">{total_contributions:,}</text>
    </g>
  </g>
  
  <!-- Footer -->
  <text x="430" y="165" text-anchor="end" fill="#484f58" font-family="Segoe UI, -apple-system, sans-serif" font-size="10" font-style="italic">Last updated: {last_updated}</text>
</svg>'''
    return svg

def main():
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not found.")
        sys.exit(1)

    try:
        print(f"🚀 Fetching activity for {USERNAME} in {YEAR}...")
        days_with_activity, total_contributions = fetch_contribution_days(USERNAME, YEAR, GITHUB_TOKEN)
        days_elapsed = calculate_days_elapsed(YEAR)
        
        print(f"📊 Stats: {days_with_activity} active days, {total_contributions} contributions, {days_elapsed} days elapsed.")
        
        svg_content = generate_svg(days_with_activity, total_contributions, days_elapsed, YEAR)
        
        with open(OUTFILE, "w") as f:
            f.write(svg_content)
        
        print(f"✅ Successfully generated {OUTFILE} (matched to visual graph)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
