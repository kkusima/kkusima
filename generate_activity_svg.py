import requests
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Constants
USER = 'kkusima'
YEAR = 2026

# Fetch commit data from GitHub API
def fetch_commit_data(user, year):
    url = f'https://api.github.com/users/{user}/events'
    headers = {'Authorization': 'token YOUR_GITHUB_TOKEN'}  # replace with a valid token
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Process commit data to count commits per day
def count_commits_per_day(data):
    commit_counts = {}
    for event in data:
        if event['type'] == 'PushEvent':
            date = event['created_at'][:10]  # Extract date
            if date not in commit_counts:
                commit_counts[date] = 0
            commit_counts[date] += len(event['payload']['commits'])
    return commit_counts

# Generate SVG visualization
def generate_svg(commit_counts):
    days = list(range(1, 32))
    weeks = list(range(1, 6))
    color_map = plt.get_cmap('YlGn')
    fig, ax = plt.subplots(figsize=(8, 6))

    for week in weeks:
        for day in days:
            date = f'{YEAR}-01-{day:02d}'  # example for January
            commits = commit_counts.get(date, 0)
            color = color_map(min(commits / 10, 1))  # Normalize commit count for color
            rect = mpatches.Rectangle((day - 1, 5 - week), 0.8, 0.8, color=color)
            ax.add_patch(rect)
            ax.text(day - 0.5, 5 - week + 0.5, str(commits), ha='center', va='center')

    ax.set_xlim(0, 31)
    ax.set_ylim(0, 5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Activity Intensity Contribution Calendar')

    plt.savefig('contribution_calendar.svg', format='svg')
    plt.close(fig)

# Main execution
if __name__ == '__main__':
    data = fetch_commit_data(USER, YEAR)
    commit_counts = count_commits_per_day(data)
    generate_svg(commit_counts)