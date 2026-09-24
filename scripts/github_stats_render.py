from datetime import date
from html import escape
from pathlib import Path
from github_stats_months import month_bars

PALETTE = ("#20303a", "#1c4d5b", "#1b7287", "#299cb2", "#67d8ef")
TEMPLATE = Path(__file__).with_name("github_stats_template.svg")


def heatmap(days):
    first = date.fromisoformat(min(days))
    boxes, labels, seen = [], [], set()
    for day, values in sorted(days.items()):
        when = date.fromisoformat(day)
        week = (when - first).days // 7
        row = (when.weekday() + 1) % 7
        x, y = 48 + 16 * week, 317 + 16 * row
        level = max(0, min(4, values["level"]))
        boxes.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{PALETTE[level]}"/>')
        month = when.strftime("%b %Y")
        if when.day <= 7 and month not in seen:
            labels.append(f'<text x="{x}" y="452" class="small muted">{when:%b}</text>')
            seen.add(month)
    return "".join(boxes), "".join(labels)


def language_bars(languages):
    peak = max((count for _, count in languages), default=1)
    parts = []
    for i, (name, count) in enumerate(languages):
        y = 598 + 28 * i
        parts.append(f'<text x="50" y="{y}" class="small ink">{escape(name)}</text>')
        parts.append(f'<rect x="224" y="{y-10}" width="{round(185*count/peak)}" height="9" rx="4" fill="{PALETTE[4-i]}"/>')
        parts.append(f'<text x="422" y="{y}" text-anchor="end" class="small muted">{count}</text>')
    return "".join(parts)


def render(stats):
    boxes, months = heatmap(stats["days"])
    replacements = {
        "CONTRIBUTIONS": stats["contributions"], "REPOS": stats["repos"],
        "ORIGINAL": stats["original"], "STARS": stats["stars"],
        "FOLLOWERS": stats["followers"], "UPDATED": stats["updated"],
        "HEATMAP": boxes, "MONTH_LABELS": months,
        "LANGUAGE_BARS": language_bars(stats["languages"]),
        "MONTH_BARS": month_bars(stats["months"]),
    }
    svg = TEMPLATE.read_text(encoding="utf-8")
    for name, value in replacements.items():
        svg = svg.replace("{{" + name + "}}", str(value))
    return svg
