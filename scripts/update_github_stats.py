from pathlib import Path
from github_stats_data import get_stats
from github_stats_render import render

root = Path(__file__).resolve().parents[1]
stats = get_stats()
target = root / "assets" / "github-stats.svg"
target.write_text(render(stats), encoding="utf-8")
print(f"Updated {target.name}: {stats['contributions']} contributions, {stats['repos']} repos")
