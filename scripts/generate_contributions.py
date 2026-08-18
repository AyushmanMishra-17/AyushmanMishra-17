import json
import os
import requests
from datetime import datetime

USERNAME = "AyushmanMishra-17"

URL = f"https://github.com/users/{USERNAME}/contributions"

response = requests.get(
    URL,
    headers={"User-Agent": "GitHub-Profile-Generator"},
    timeout=20
)

response.raise_for_status()

html = response.text

# Save the raw page for debugging/reference
os.makedirs("data", exist_ok=True)

with open("data/github_contributions.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Contribution data fetched for {USERNAME}")
print(f"Updated: {datetime.utcnow().isoformat()}Z")