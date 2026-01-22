import svgwrite
import datetime
import random

def generate_contribution_calendar(year):
    # Create an SVG drawing
    dwg = svgwrite.Drawing('days-2026.svg', profile='tiny', size=(800, 200))
    # Define colors based on intensity
    colors = {"1": '#d9f7be', "2": '#a0e8a4', "3": '#68c48a', "4": '#34a853', "5": '#0f9d58', "0": '#ffffff'}
    # Set grid parameters
    cols = 53  # Number of columns for weeks
    rows = 7   # Total number of rows for days of the week
    cell_size = 15
    margin = 2

    # Draw the grid
    for week in range(cols):
        for day in range(rows):
            # Random intensity from 0 to 5
            intensity = random.randint(0, 5)
            # Color for the current cell based on intensity
            color = colors[str(intensity)]
            # Add a rectangle for each cell
            dwg.add(dwg.rect(insert=(week * (cell_size + margin), day * (cell_size + margin)),
                             size=(cell_size, cell_size),
                             fill=color))

    # Save the SVG file
    dwg.save()

generate_contribution_calendar(2026)