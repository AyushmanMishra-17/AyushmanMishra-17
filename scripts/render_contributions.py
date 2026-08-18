from bs4 import BeautifulSoup
from pathlib import Path
from html import escape
import re

INPUT = Path("data/github_contributions.html")
OUTPUT = Path("assets/contribution-heatmap.svg")

WIDTH = 900
CELL = 12
GAP = 3
TOP = 45
LEFT = 35

html = INPUT.read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

# GitHub contribution cells
cells = soup.select("td.ContributionCalendar-day")

if not cells:
    # Fallback for GitHub's current markup
    cells = soup.select("[data-level]")

if not cells:
    raise RuntimeError(
        "Could not find GitHub contribution cells in the downloaded HTML."
    )

# Extract contribution information
contributions = []

for cell in cells:
    level = cell.get("data-level", "0")

    title = cell.get("title", "")

    if not title:
        title_tag = cell.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    # Try to extract date
    date = cell.get("data-date", "")

    if not date:
        text = cell.get_text(" ", strip=True)
        match = re.search(r"\d{4}-\d{2}-\d{2}", text)
        if match:
            date = match.group(0)

    try:
        level = int(level)
    except ValueError:
        level = 0

    contributions.append({
        "level": level,
        "title": title,
        "date": date
    })


# GitHub normally returns 53 weeks × 7 days.
# Organize cells by their order in the calendar.
columns = []

for i in range(0, len(contributions), 7):
    columns.append(contributions[i:i + 7])


# SVG
svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{TOP + 7 * (CELL + GAP) + 45}"
    viewBox="0 0 {WIDTH} {TOP + 7 * (CELL + GAP) + 45}">
'''
)

svg.append("""
<style>
    .cell {
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        animation: appear 0.35s ease-out forwards;
    }

    @keyframes appear {
        from {
            opacity: 0;
            transform: scale(0.2);
        }

        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    .label {
        font-family: monospace;
        font-size: 13px;
        fill: #8b949e;
    }
</style>
""")


# Header
svg.append(
    '<text x="35" y="25" class="label">'
    'GITHUB CONTRIBUTION ACTIVITY'
    '</text>'
)


# GitHub-style levels
levels = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}


# Draw cells
animation_index = 0

for x, column in enumerate(columns):

    for y, contribution in enumerate(column):

        level = contribution["level"]

        color = levels.get(level, levels[4])

        px = LEFT + x * (CELL + GAP)
        py = TOP + y * (CELL + GAP)

        delay = animation_index * 0.012

        title = escape(contribution["title"])

        svg.append(
            f'''
            <rect
                class="cell"
                x="{px}"
                y="{py}"
                width="{CELL}"
                height="{CELL}"
                rx="2"
                fill="{color}"
                style="animation-delay:{delay:.3f}s"
            >
                <title>{title}</title>
            </rect>
            '''
        )

        animation_index += 1


# Legend
legend_y = TOP + 7 * (CELL + GAP) + 22

svg.append(
    f'<text x="{LEFT}" y="{legend_y}" class="label">Less</text>'
)

legend_x = LEFT + 40

for level in range(5):

    color = levels[level]

    svg.append(
        f'''
        <rect
            x="{legend_x + level * 18}"
            y="{legend_y - 11}"
            width="12"
            height="12"
            rx="2"
            fill="{color}"
        />
        '''
    )

svg.append(
    f'<text x="{legend_x + 105}" y="{legend_y}" class="label">More</text>'
)

svg.append("</svg>")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

OUTPUT.write_text(
    "".join(svg),
    encoding="utf-8"
)

print(f"Generated: {OUTPUT}")
print(f"Contribution cells: {len(contributions)}")