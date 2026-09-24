from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from html.parser import HTMLParser
import json
import re
from urllib.request import Request, urlopen

USER = "CYBORG-YASHRAJ"
HEADERS = {"User-Agent": "CYBORG-YASHRAJ-profile-report", "Accept": "application/vnd.github+json"}


def fetch(url):
    with urlopen(Request(url, headers=HEADERS), timeout=25) as response:
        return response.read().decode("utf-8")


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.current = None
        self.tooltip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs:
            self.current = attrs["data-date"]
            self.days[self.current] = {"level": int(attrs.get("data-level", 0)), "count": 0}
        elif tag == "tool-tip" and self.current:
            self.tooltip, self.parts = True, []

    def handle_data(self, data):
        if self.tooltip:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.tooltip:
            match = re.search(r"([\d,]+) contributions? on", "".join(self.parts))
            if match:
                self.days[self.current]["count"] = int(match.group(1).replace(",", ""))
            self.tooltip = False


def get_stats():
    base = f"https://api.github.com/users/{USER}"
    profile = json.loads(fetch(base))
    repos = json.loads(fetch(base + "/repos?per_page=100&type=owner"))
    source = fetch(f"https://github.com/users/{USER}/contributions")
    calendar = Calendar()
    calendar.feed(source)
    total = re.search(r"([\d,]+)\s+contributions\s+in the last year", source)
    if profile.get("login", "").lower() != USER.lower() or len(calendar.days) < 360 or not total:
        raise ValueError("GitHub returned incomplete profile or calendar data")
    original = [repo for repo in repos if not repo["fork"]]
    languages = Counter(repo["language"] for repo in original if repo["language"])
    months = defaultdict(int)
    for day, values in calendar.days.items():
        months[day[:7]] += values["count"]
    return {
        "updated": datetime.now(timezone.utc).strftime("%d %b %Y UTC"),
        "contributions": int(total.group(1).replace(",", "")),
        "repos": profile["public_repos"],
        "original": len(original),
        "stars": sum(repo["stargazers_count"] for repo in repos),
        "followers": profile["followers"],
        "days": calendar.days,
        "languages": languages.most_common(5),
        "months": [(date.fromisoformat(key + "-01").strftime("%b"), months[key]) for key in sorted(months)[-12:]],
    }
