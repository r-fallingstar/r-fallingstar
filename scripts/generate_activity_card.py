"""Fetch GitHub contributions and generate light/dark JA/EN activity cards."""

from datetime import date, datetime
from pathlib import Path
import re
import urllib.request

USERNAME = "r-fallingstar"
FONT_FAMILY = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', "
    "'Hiragino Sans', 'Yu Gothic UI', 'Meiryo', 'Noto Sans JP', sans-serif"
)

THEMES = {
    "light": {
        "card_bg_start": "#FEFCFF",
        "card_bg_end": "#FAF4FC",
        "card_border": "#E6D7EE",
        "primary_ink": "#4B3759",
        "secondary_ink": "#6B547A",
        "muted_ink": "#8B719C",
        "accent_start": "#B79AD6",
        "accent_end": "#E49EC2",
        "stroke_color": "#B37BB3",
        "wave_color": "#D8A8DC",
        "wave_top_opacity": "0.42",
        "wave_bottom_opacity": "0.02",
        "ring_fill": "#FAF2FC",
        "ring_halo": "#FCF7FE",
        "gem_fill": "#E49EC2",
        "divider": "#EFE3F5",
        "grid": "#F2E9F6",
        "peak_dot_ring": "#FFFFFF",
        "sparkle": "#C9A8DF",
        "dots": ("#E49EC2", "#B79AD6", "#9CB8E2", "#9CC9B0"),
    },
    "dark": {
        "card_bg_start": "#1A1625",
        "card_bg_end": "#20182B",
        "card_border": "#3B2E4E",
        "primary_ink": "#F4ECF8",
        "secondary_ink": "#CFC0DB",
        "muted_ink": "#A490B5",
        "accent_start": "#C7A9EA",
        "accent_end": "#F2ADCE",
        "stroke_color": "#DF9ED2",
        "wave_color": "#DDA9D5",
        "wave_top_opacity": "0.36",
        "wave_bottom_opacity": "0.03",
        "ring_fill": "#221B30",
        "ring_halo": "#1D1729",
        "gem_fill": "#F2ADCE",
        "divider": "#302642",
        "grid": "#2A223B",
        "peak_dot_ring": "#1D1729",
        "sparkle": "#C7A9EA",
        "dots": ("#F2ADCE", "#C7A9EA", "#A2BCE8", "#9FD3B8"),
    },
}

MONTH_EN = (
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def fetch_contributions(username: str) -> list[tuple[str, int]]:
    """Fetch daily contribution counts for the past year from GitHub."""
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8")

    cells = dict(
        re.findall(
            r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[^"]+)"',
            html,
        )
    )
    tips = dict(
        re.findall(
            r'for="(contribution-day-component-[^"]+)"[^>]*>([^<]+)</tool-tip>',
            html,
        )
    )

    records: list[tuple[str, int]] = []
    for date_str, cid in cells.items():
        tip = tips.get(cid, "")
        cnt = 0
        m = re.search(r"(\d+)\s+contribution", tip)
        if m:
            cnt = int(m.group(1))
        records.append((date_str, cnt))

    records.sort(key=lambda item: item[0])
    return records


def compute_metrics(records: list[tuple[str, int]]) -> dict:
    """Compute summary metrics and streak info from sorted daily records."""
    if not records:
        today = date.today().isoformat()
        return {
            "total": 0,
            "active_days": 0,
            "last_30": 0,
            "longest": 0,
            "streak": 0,
            "is_active_streak": False,
            "updated_date": today,
        }

    total = sum(cnt for _, cnt in records)
    active_days = sum(1 for _, cnt in records if cnt > 0)
    last_30 = sum(cnt for _, cnt in records[-30:])

    longest = 0
    run = 0
    for _, cnt in records:
        if cnt > 0:
            run += 1
            if run > longest:
                longest = run
        else:
            run = 0

    has_recent_activity = records[-1][1] > 0 or (
        len(records) >= 2 and records[-2][1] > 0
    )
    streak = 0
    for _, cnt in reversed(records):
        if cnt > 0:
            streak += 1
        elif streak == 0:
            continue
        else:
            break

    return {
        "total": total,
        "active_days": active_days,
        "last_30": last_30,
        "longest": longest,
        "streak": streak,
        "is_active_streak": has_recent_activity,
        "updated_date": records[-1][0],
    }


def build_weekly_series(records: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """Aggregate daily counts into 7-day chunks tagged with the chunk's end date."""
    if not records:
        return [(date.today().isoformat(), 0), (date.today().isoformat(), 0)]

    weekly: list[tuple[str, int]] = []
    for i in range(0, len(records), 7):
        chunk = records[i : i + 7]
        weekly.append((chunk[-1][0], sum(cnt for _, cnt in chunk)))

    if len(weekly) == 1:
        weekly.append(weekly[0])
    return weekly


def monotone_cubic_path(
    points: list[tuple[float, float]], baseline_y: float
) -> tuple[str, str]:
    """Generate Fritsch-Carlson monotone cubic Bezier SVG stroke and fill paths.

    Monotonicity ensures the curve never overshoots below baseline_y on flat zero runs.
    """
    n = len(points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    if n < 2:
        p0 = points[0]
        stroke = f"M {p0[0]:.2f} {p0[1]:.2f}"
        fill = f"{stroke} L {p0[0]:.2f} {baseline_y:.2f} Z"
        return stroke, fill

    dx = [xs[i + 1] - xs[i] for i in range(n - 1)]
    dy = [ys[i + 1] - ys[i] for i in range(n - 1)]
    slopes = [dy[i] / dx[i] if dx[i] != 0 else 0.0 for i in range(n - 1)]

    tangents = [0.0] * n
    tangents[0] = slopes[0]
    tangents[-1] = slopes[-1]
    for i in range(1, n - 1):
        if slopes[i - 1] * slopes[i] <= 0:
            tangents[i] = 0.0
        else:
            tangents[i] = (slopes[i - 1] + slopes[i]) / 2.0

    # Enforce Fritsch-Carlson monotonicity constraint
    for i in range(n - 1):
        if slopes[i] == 0.0:
            tangents[i] = 0.0
            tangents[i + 1] = 0.0
        else:
            alpha = tangents[i] / slopes[i]
            beta = tangents[i + 1] / slopes[i]
            sq = alpha * alpha + beta * beta
            if sq > 9.0:
                tau = 3.0 / (sq ** 0.5)
                tangents[i] = tau * alpha * slopes[i]
                tangents[i + 1] = tau * beta * slopes[i]

    segments = [f"M {xs[0]:.2f} {ys[0]:.2f}"]
    for i in range(n - 1):
        h = dx[i] / 3.0
        c1x = xs[i] + h
        c1y = min(baseline_y, ys[i] + tangents[i] * h)
        c2x = xs[i + 1] - h
        c2y = min(baseline_y, ys[i + 1] - tangents[i + 1] * h)
        segments.append(
            f"C {c1x:.2f} {c1y:.2f}, {c2x:.2f} {c2y:.2f}, {xs[i + 1]:.2f} {ys[i + 1]:.2f}"
        )

    stroke_path = " ".join(segments)
    fill_path = (
        f"{stroke_path} L {xs[-1]:.2f} {baseline_y:.2f} "
        f"L {xs[0]:.2f} {baseline_y:.2f} Z"
    )
    return stroke_path, fill_path


def format_month(date_str: str, lang: str) -> str:
    """Format YYYY-MM-DD as a compact localized month label."""
    month = datetime.strptime(date_str, "%Y-%m-%d").month
    return f"{month}月" if lang == "ja" else MONTH_EN[month]


def build_month_ticks(
    weekly: list[tuple[str, int]],
    graph_x: float,
    graph_w: float,
    lang: str,
) -> list[tuple[float, str, str]]:
    """Compute non-overlapping evenly-spaced x-axis month labels plus 'Now'."""
    n = len(weekly)
    ticks: list[tuple[float, str, str]] = []
    # 6 evenly-spaced historical ticks across 0%..84% of the axis, plus 'Now' at 100%
    fractions = (0.0, 0.165, 0.335, 0.50, 0.665, 0.83)
    prev_label = None
    for idx_pos, frac in enumerate(fractions):
        wk_idx = min(n - 1, round(frac * (n - 1)))
        x = graph_x + (wk_idx / (n - 1)) * graph_w
        label = format_month(weekly[wk_idx][0], lang)
        if label == prev_label and idx_pos > 0:
            # Shift slightly to next distinct month if chunk spacing lands on same month
            alt_idx = min(n - 1, wk_idx + 2)
            alt_label = format_month(weekly[alt_idx][0], lang)
            if alt_label != prev_label:
                label = alt_label
        prev_label = label
        anchor = "start" if idx_pos == 0 else "middle"
        ticks.append((x, label, anchor))

    now_label = "現在" if lang == "ja" else "Now"
    ticks.append((graph_x + graph_w, now_label, "end"))
    return ticks


def render_svg(
    metrics: dict,
    weekly: list[tuple[str, int]],
    lang: str,
    theme_name: str,
) -> str:
    """Render one localized light/dark activity SVG card (820x276)."""
    t = THEMES[theme_name]
    graph_x = 264.0
    graph_y = 158.0
    graph_w = 520.0
    graph_h = 74.0
    baseline_y = graph_y + graph_h  # 232.0

    values = [val for _, val in weekly]
    max_val = max(max(values), 1)
    n = len(weekly)

    points: list[tuple[float, float]] = []
    for i, val in enumerate(values):
        x = graph_x + (i / (n - 1)) * graph_w
        y = baseline_y - (val / max_val) * (graph_h - 6.0)
        points.append((x, y))

    stroke_path, fill_path = monotone_cubic_path(points, baseline_y)

    # Peak marker coordinates (pick latest occurrence if tied)
    peak_idx = len(values) - 1 - values[::-1].index(max(values))
    peak_x, peak_y = points[peak_idx]
    has_peak = max(values) > 0

    ticks = build_month_ticks(weekly, graph_x, graph_w, lang)
    ticks_markup = "\n".join(
        f'    <text x="{x:.1f}" y="250" text-anchor="{anchor}">{label}</text>'
        for x, label, anchor in ticks
    )

    if lang == "ja":
        aria = "GitHub 開発アクティビティ統計"
        total_label = "年間コントリビューション"
        total_sub = "過去1年間の活動合計"
        streak_label = (
            "現在の継続日数" if metrics["is_active_streak"] else "直近の継続日数"
        )
        streak_unit = "日"
        longest_label = "最長継続日数"
        longest_sub = "自己ベスト記録"
        rows = (
            f"直近30日：{metrics['last_30']} 件",
            f"活動日数：{metrics['active_days']} 日 / 年",
            "拠点：福井県, 日本",
            f"更新：{metrics['updated_date']}",
        )
        chart_title = "過去1年間のアクティビティ推移（週別）"
        peak_text = f"週最大 {max(values)} 件"
    else:
        aria = "GitHub activity statistics"
        total_label = "Yearly Contributions"
        total_sub = "Total over the past year"
        streak_label = (
            "Current Streak" if metrics["is_active_streak"] else "Recent Streak"
        )
        streak_unit = "d"
        longest_label = "Longest Streak"
        longest_sub = "Personal best"
        rows = (
            f"Last 30 days: {metrics['last_30']}",
            f"Active days: {metrics['active_days']} / yr",
            "Based in Fukui, Japan",
            f"Updated: {metrics['updated_date']}",
        )
        chart_title = "Weekly Activity (Past 12 Months)"
        peak_text = f"Peak {max(values)} / wk"

    streak_sub = "連続記録" if lang == "ja" else "Consecutive days"
    if not metrics["is_active_streak"]:
        streak_sub = "直近の連続記録" if lang == "ja" else "Most recent run"

    snapshot_rows = []
    for idx, (row_text, dot_color) in enumerate(zip(rows, t["dots"])):
        y = 156 + idx * 26
        weight = ' font-weight="600"' if idx == 0 else ""
        snapshot_rows.append(
            f'    <circle cx="42" cy="{y - 4}" r="3.5" fill="{dot_color}" />\n'
            f'    <text x="54" y="{y}"{weight}>{row_text}</text>'
        )
    snapshot_markup = "\n".join(snapshot_rows)

    peak_markup = ""
    if has_peak:
        peak_markup = (
            f'  <circle cx="{peak_x:.2f}" cy="{peak_y:.2f}" r="5.5" fill="{t["accent_end"]}" opacity="0.28" />\n'
            f'  <circle cx="{peak_x:.2f}" cy="{peak_y:.2f}" r="3" fill="{t["accent_end"]}" stroke="{t["peak_dot_ring"]}" stroke-width="1.2" />'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="276" viewBox="0 0 820 276" role="img" aria-label="{aria}">
  <defs>
    <linearGradient id="card-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['card_bg_start']}" />
      <stop offset="100%" stop-color="{t['card_bg_end']}" />
    </linearGradient>
    <linearGradient id="wave-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{t['wave_color']}" stop-opacity="{t['wave_top_opacity']}" />
      <stop offset="100%" stop-color="{t['wave_color']}" stop-opacity="{t['wave_bottom_opacity']}" />
    </linearGradient>
    <linearGradient id="ring-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{t['accent_start']}" />
      <stop offset="100%" stop-color="{t['accent_end']}" />
    </linearGradient>
    <linearGradient id="line-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent_start']}" />
      <stop offset="100%" stop-color="{t['stroke_color']}" />
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="818" height="274" rx="18" fill="url(#card-bg)" stroke="{t['card_border']}" stroke-width="1.25" />

  <!-- Subtle corner starlight sparkles -->
  <path d="M 789 17 L 790.5 21.5 L 795 23 L 790.5 24.5 L 789 29 L 787.5 24.5 L 783 23 L 787.5 21.5 Z" fill="{t['sparkle']}" opacity="0.38" />
  <circle cx="775" cy="28" r="1.4" fill="{t['gem_fill']}" opacity="0.35" />

  <!-- Top KPI 1: Total Contributions -->
  <g text-anchor="middle" font-family="{FONT_FAMILY}">
    <text x="145" y="56" font-size="30" font-weight="700" fill="{t['primary_ink']}">{metrics['total']}</text>
    <text x="145" y="82" font-size="12" font-weight="600" fill="{t['secondary_ink']}">{total_label}</text>
    <text x="145" y="100" font-size="10.5" fill="{t['muted_ink']}">{total_sub}</text>
  </g>

  <line x1="282" y1="26" x2="282" y2="108" stroke="{t['divider']}" stroke-width="1" />

  <!-- Top KPI 2: Streak Ring -->
  <g text-anchor="middle" font-family="{FONT_FAMILY}">
    <circle cx="410" cy="48" r="26" fill="{t['ring_fill']}" stroke="url(#ring-grad)" stroke-width="3.2" />
    <circle cx="410" cy="22" r="5.8" fill="{t['ring_halo']}" />
    <path d="M 410 16.8 L 411.4 20.6 L 415.2 22 L 411.4 23.4 L 410 27.2 L 408.6 23.4 L 404.8 22 L 408.6 20.6 Z" fill="{t['gem_fill']}" />
    <text x="410" y="56" font-size="21" font-weight="700" fill="{t['primary_ink']}">{metrics['streak']}<tspan font-size="11.5" font-weight="600" fill="{t['secondary_ink']}">{streak_unit}</tspan></text>
    <text x="410" y="92" font-size="12" font-weight="600" fill="{t['secondary_ink']}">{streak_label}</text>
    <text x="410" y="108" font-size="10.5" fill="{t['muted_ink']}">{streak_sub}</text>
  </g>

  <line x1="538" y1="26" x2="538" y2="108" stroke="{t['divider']}" stroke-width="1" />

  <!-- Top KPI 3: Longest Streak -->
  <g text-anchor="middle" font-family="{FONT_FAMILY}">
    <text x="675" y="56" font-size="30" font-weight="700" fill="{t['primary_ink']}">{metrics['longest']}<tspan font-size="14" font-weight="600" fill="{t['secondary_ink']}">{streak_unit}</tspan></text>
    <text x="675" y="82" font-size="12" font-weight="600" fill="{t['secondary_ink']}">{longest_label}</text>
    <text x="675" y="100" font-size="10.5" fill="{t['muted_ink']}">{longest_sub}</text>
  </g>

  <line x1="32" y1="124" x2="788" y2="124" stroke="{t['divider']}" stroke-width="1" />

  <!-- Bottom Left: Snapshot Summary -->
  <g font-family="{FONT_FAMILY}" font-size="12" fill="{t['secondary_ink']}">
{snapshot_markup}
  </g>

  <!-- Bottom Right: Weekly Activity Area Chart -->
  <g font-family="{FONT_FAMILY}">
    <text x="264" y="146" font-size="11" font-weight="600" fill="{t['secondary_ink']}">{chart_title}</text>
    <text x="784" y="146" text-anchor="end" font-size="10.5" fill="{t['muted_ink']}">{peak_text}</text>
  </g>

  <line x1="264" y1="158" x2="784" y2="158" stroke="{t['grid']}" stroke-width="1" stroke-dasharray="3 4" />
  <line x1="264" y1="195" x2="784" y2="195" stroke="{t['grid']}" stroke-width="1" stroke-dasharray="3 4" />

  <path d="{fill_path}" fill="url(#wave-grad)" />
  <path d="{stroke_path}" fill="none" stroke="url(#line-grad)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />
{peak_markup}

  <line x1="264" y1="232" x2="784" y2="232" stroke="{t['divider']}" stroke-width="1.2" />

  <g font-family="{FONT_FAMILY}" font-size="10" fill="{t['muted_ink']}">
{ticks_markup}
  </g>
</svg>
'''


def main() -> None:
    records = fetch_contributions(USERNAME)
    metrics = compute_metrics(records)
    weekly = build_weekly_series(records)

    assets_dir = Path("assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    for lang in ("ja", "en"):
        for theme in ("light", "dark"):
            out_path = assets_dir / f"activity-card-{lang}-{theme}.svg"
            out_path.write_text(
                render_svg(metrics, weekly, lang, theme),
                encoding="utf-8",
            )
            print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
