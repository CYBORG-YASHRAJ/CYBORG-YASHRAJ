from html import escape


def month_bars(months):
    peak = max((count for _, count in months), default=1)
    parts = []
    for i, (name, count) in enumerate(months):
        x = 518 + 33 * i
        height = round(112 * count / peak)
        color = "#67d8ef" if count == peak else "#1b7287"
        parts.append(f'<rect x="{x}" y="{710-height}" width="21" height="{height}" rx="4" fill="{color}"/>')
        parts.append(f'<text x="{x+10}" y="732" text-anchor="middle" class="tiny muted">{escape(name)}</text>')
    return "".join(parts)
