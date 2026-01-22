#!/usr/bin/env python3
"""
Generate a clean SVG showing the number of days with commits in 2026.
Uses GitHub GraphQL API to fetch contribution data.
"""

import os
import requests
from datetime import datetime

GITHUB_TOKEN = os. environ.get("GITHUB_TOKEN")
USERNAME = "kkusima"
YEAR = 2026


def fetch_contribution_days():
    """Fetch the number of days with contributions in the specified year using GraphQL."""
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
        "username": USERNAME,
        "from": f"{YEAR}-01-01T00:00:00Z",
        "to": f"{YEAR}-12-31T23:59:59Z"
    }
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )
    response.raise_for_status()
    data = response.json()
    
    # Count days with at least one contribution
    days_with_commits = 0
    total_contributions = 0
    
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    for week in weeks: 
        for day in week["contributionDays"]:
            if day["contributionCount"] > 0:
                days_with_commits += 1
            total_contributions += day["contributionCount"]
    
    return days_with_commits, total_contributions


def calculate_days_elapsed():
    """Calculate the number of days elapsed in the year so far."""
    today = datetime.now()
    if today.year == YEAR: 
        start_of_year = datetime(YEAR, 1, 1)
        return (today - start_of_year).days + 1
    elif today.year > YEAR:
        return 366 if (YEAR % 4 == 0 and (YEAR % 100 != 0 or YEAR % 400 == 0)) else 365
    else:
        return 0


def generate_svg(days_with_commits, total_contributions, days_elapsed):
    """Generate a clean, modern SVG displaying commit day statistics."""
    
    # Calculate percentage
    percentage = (days_with_commits / days_elapsed * 100) if days_elapsed > 0 else 0
    
    # Determine the ring color based on percentage
    if percentage >= 80:
        ring_color = "#40c463"  # Green - excellent
    elif percentage >= 60:
        ring_color = "#9be9a8"  # Light green - good
    elif percentage >= 40:
        ring_color = "#ffd33d"  # Yellow - moderate
    else:
        ring_color = "#f97583"  # Red - needs work
    
    # Calculate the stroke-dasharray for the progress ring
    circumference = 2 * 3.14159 * 54  # radius = 54
    progress_length = (percentage / 100) * circumference
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="160" viewBox="0 0 400 160">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d1117;stop-opacity: 1" />
      <stop offset="100%" style="stop-color:#161b22;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="400" height="160" rx="12" fill="url(#bgGrad)" stroke="#30363d" stroke-width="1"/>
  
  <!-- Progress Ring -->
  <g transform="translate(80, 80)">
    <!-- Background ring -->
    <circle cx="0" cy="0" r="54" fill="none" stroke="#21262d" stroke-width="8"/>
    <!-- Progress ring -->
    <circle cx="0" cy="0" r="54" fill="none" stroke="{ring_color}" stroke-width="8"
            stroke-dasharray="{progress_length:.1f} {circumference:.1f}"
            stroke-linecap="round" transform="rotate(-90)"/>
    <!-- Center text -->
    <text x="0" y="-8" text-anchor="middle" fill="#ffffff" font-family="Segoe UI, sans-serif" font-size="28" font-weight="bold">{days_with_commits}</text>
    <text x="0" y="14" text-anchor="middle" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="11">days</text>
  </g>
  
  <!-- Stats -->
  <g transform="translate(170, 45)">
    <text x="0" y="0" fill="#58a6ff" font-family="Segoe UI, sans-serif" font-size="14" font-weight="600">📅 {YEAR} Commit Activity</text>
    
    <text x="0" y="32" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="12">Days with commits</text>
    <text x="0" y="50" fill="#ffffff" font-family="Segoe UI, sans-serif" font-size="16" font-weight="500">{days_with_commits} / {days_elapsed}</text>
    
    <text x="0" y="78" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="12">Total contributions</text>
    <text x="0" y="96" fill="#ffffff" font-family="Segoe UI, sans-serif" font-size="16" font-weight="500">{total_contributions:,}</text>
  </g>
  
  <!-- Consistency badge -->
  <g transform="translate(320, 130)">
    <text x="0" y="0" text-anchor="end" fill="#8b949e" font-family="Segoe UI, sans-serif" font-size="10">{percentage:.0f}% consistency</text>
  </g>
</svg>'''
    
    return svg


def main():
    days_with_commits, total_contributions = fetch_contribution_days()
    days_elapsed = calculate_days_elapsed()
    
    svg_content = generate_svg(days_with_commits, total_contributions, days_elapsed)
    
    with open("commit-activity.svg", "w") as f:
        f.write(svg_content)
    
    print(f"✅ Generated commit-activity.svg")
    print(f"   Days with commits: {days_with_commits}/{days_elapsed}")
    print(f"   Total contributions: {total_contributions}")


if __name__ == "__main__": 
    main()
