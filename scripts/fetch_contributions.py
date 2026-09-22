"""Fetch the public GitHub contribution calendar without an API token."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

USERNAME = "Godleads1"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path("data/contributions.json")


class ContributionParser(HTMLParser):
    """Parse contribution-day attributes from GitHub's public calendar."""

    def __init__(self) -> None:
        super().__init__()
        self.days: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect a valid contribution cell from the HTML fragment."""
        values = dict(attrs)
        date = values.get("data-date")
        level = values.get("data-level")
        if not date or level is None:
            return
        try:
            parsed_level = max(0, min(4, int(level)))
        except ValueError:
            return
        self.days.append({"date": date, "level": parsed_level})


def main() -> None:
    """Fetch, validate, and store the latest public contribution calendar."""
    request = Request(
        URL,
        headers={
            "Accept": "text/html",
            "User-Agent": "Godleads1-profile-workflow/1.0",
        },
    )
    with urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8")

    parser = ContributionParser()
    parser.feed(body)
    unique_days = {str(day["date"]): day for day in parser.days}
    days = [unique_days[key] for key in sorted(unique_days)]

    if len(days) < 300:
        raise RuntimeError(
            f"Expected a contribution year, but GitHub returned {len(days)} days."
        )

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days[-371:],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
