"""Render the saved GitHub contribution levels as a self-contained animated SVG."""

from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path

INPUT = Path("data/contributions.json")
OUTPUT = Path("assets/contributions.svg")
PALETTE = ["#13212d", "#0f4c45", "#0d7668", "#14a38e", "#5eead4"]


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    records = [
        (date.fromisoformat(item["date"]), int(item["level"]))
        for item in payload["days"]
    ]
    records.sort(key=lambda item: item[0])
    start = records[0][0]
    activity_days = sum(level > 0 for _, level in records)

    boxes: list[str] = []
    for current, level in records:
        offset = (current - start).days
        week, weekday = divmod(offset, 7)
        x, y = 44 + week * 14, 54 + weekday * 14
        delay = min(week * 0.018 + weekday * 0.012, 1.2)
        boxes.append(
            f'<rect class="day" x="{x}" y="{y}" width="10" height="10" rx="2" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"/>'
        )

    username = escape(str(payload["username"]))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" viewBox="0 0 860 190" role="img" aria-labelledby="title desc">
<title id="title">{username} contribution activity</title>
<desc id="desc">GitHub contribution levels over the last 53 weeks; {activity_days} active days.</desc>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.day{{opacity:0;transform:translateY(-8px);animation:arrive .38s ease-out forwards}}
@keyframes arrive{{to{{opacity:1;transform:translateY(0)}}}}
@media(prefers-reduced-motion:reduce){{.day{{animation:none;opacity:1;transform:none}}}}
</style>
<rect width="860" height="190" rx="16" fill="#050b12"/>
<rect x="1" y="1" width="858" height="188" rx="15" fill="none" stroke="#1d4059"/>
<text x="34" y="32" fill="#5eead4" font-size="13">$ contributions --last=53w --user={username}</text>
{"".join(boxes)}
<text x="44" y="172" fill="#7896aa" font-size="12">{activity_days} active days in the displayed period</text>
<text x="685" y="172" fill="#7896aa" font-size="11">less</text>
{"".join(f'<rect x="{720 + index * 14}" y="163" width="10" height="10" rx="2" fill="{color}"/>' for index, color in enumerate(PALETTE))}
<text x="797" y="172" fill="#7896aa" font-size="11">more</text>
</svg>
"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
