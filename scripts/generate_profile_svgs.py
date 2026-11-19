"""Generate static light/dark profile SVGs for r-fallingstar."""

from pathlib import Path

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
        "divider_line": "#EFE3F5",
        "focus_cards": [
            {
                "bg_start": "#F9F5FE",
                "bg_end": "#F4ECFB",
                "border": "#E4D5F3",
                "icon_bg": "#EDE2F9",
                "icon_stroke": "#7C629C",
                "tag_bg": "#EFE6FA",
                "tag_ink": "#7B619B",
            },
            {
                "bg_start": "#FDF7FB",
                "bg_end": "#FBEFF6",
                "border": "#F0D5E6",
                "icon_bg": "#F9E4F0",
                "icon_stroke": "#A45E85",
                "tag_bg": "#FBEAF3",
                "tag_ink": "#9F5B81",
            },
            {
                "bg_start": "#F7F6FE",
                "bg_end": "#F4EEF9",
                "border": "#E2D6F2",
                "icon_bg": "#ECE5FA",
                "icon_stroke": "#73609E",
                "tag_bg": "#EFEAF9",
                "tag_ink": "#73609E",
            },
        ],
        "pills": {
            "lavender": {"bg": "#F5EFFB", "border": "#E3D4F1", "ink": "#4B3759"},
            "blush": {"bg": "#FCEFF5", "border": "#F2D2E2", "ink": "#4B3759"},
            "periwinkle": {"bg": "#F0F2FB", "border": "#D8DFF3", "ink": "#4B3759"},
        },
        "sponsor": {
            "bg_start": "#F9F1FE",
            "bg_end": "#FDF0F6",
            "border": "#E5CCE7",
            "heart": "#D57FA9",
            "ink": "#4B3759",
            "arrow": "#8B719C",
        },
        "star_fill": "#C9A8DF",
        "star_dot": "#E49EC2",
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
        "divider_line": "#302642",
        "focus_cards": [
            {
                "bg_start": "#1D182B",
                "bg_end": "#211B31",
                "border": "#3C3157",
                "icon_bg": "#2B2241",
                "icon_stroke": "#CBB2EE",
                "tag_bg": "#28203D",
                "tag_ink": "#CBB2EE",
            },
            {
                "bg_start": "#221828",
                "bg_end": "#271B2E",
                "border": "#4B324D",
                "icon_bg": "#362238",
                "icon_stroke": "#F2B3D1",
                "tag_bg": "#332035",
                "tag_ink": "#F2B3D1",
            },
            {
                "bg_start": "#1B192B",
                "bg_end": "#211C32",
                "border": "#3A3359",
                "icon_bg": "#282442",
                "icon_stroke": "#C5BDF2",
                "tag_bg": "#26223E",
                "tag_ink": "#C5BDF2",
            },
        ],
        "pills": {
            "lavender": {"bg": "#251E35", "border": "#43365E", "ink": "#F4ECF8"},
            "blush": {"bg": "#2E1E2D", "border": "#573853", "ink": "#F4ECF8"},
            "periwinkle": {"bg": "#1F2235", "border": "#384061", "ink": "#F4ECF8"},
        },
        "sponsor": {
            "bg_start": "#241C34",
            "bg_end": "#2D1D2E",
            "border": "#4D385C",
            "heart": "#F2ADCE",
            "ink": "#F4ECF8",
            "arrow": "#CFC0DB",
        },
        "star_fill": "#C7A9EA",
        "star_dot": "#F2ADCE",
    },
}

FOCUS_COPY = {
    "ja": {
        "aria": "関心のある分野：宇宙・衛星画像、Unity・VRChat、AIツール",
        "cards": [
            {
                "tag": "EARTH &amp; SPACE",
                "tag_w": 96,
                "title": "宇宙・衛星画像",
                "line1": "宇宙技術や衛星データから見える",
                "line2": "地球の姿を追い、解析ツールを制作",
            },
            {
                "tag": "XR &amp; WORLDS",
                "tag_w": 88,
                "title": "Unity・VRChat",
                "line1": "バーチャル空間でのものづくりや",
                "line2": "ワールド・XR 補助ツールを開発",
            },
            {
                "tag": "AI &amp; MCP",
                "tag_w": 68,
                "title": "AI ツール",
                "line1": "開発や日常作業を支える AI を活用し",
                "line2": "実用的なワークフローを模索",
            },
        ],
    },
    "en": {
        "aria": "Focus areas: Space and Satellite, Unity and VRChat, AI and MCP Tools",
        "cards": [
            {
                "tag": "EARTH &amp; SPACE",
                "tag_w": 96,
                "title": "Space &amp; Satellite",
                "line1": "Exploring Earth observation and",
                "line2": "building satellite imagery tools.",
            },
            {
                "tag": "XR &amp; WORLDS",
                "tag_w": 88,
                "title": "Unity &amp; VRChat",
                "line1": "Creating virtual spaces, worlds,",
                "line2": "and practical XR &amp; Unity helpers.",
            },
            {
                "tag": "AI &amp; MCP",
                "tag_w": 68,
                "title": "AI &amp; MCP Tools",
                "line1": "Integrating AI and MCP tools into",
                "line2": "practical everyday workflows.",
            },
        ],
    },
}


def focus_icon_svg(index: int, stroke: str) -> str:
    """Return minimalist vector icon paths positioned inside a 34x34 box at (18, 18)."""
    if index == 0:
        # Ringed planet / satellite orbit
        return f"""
      <circle cx="35" cy="35" r="7.5" fill="none" stroke="{stroke}" stroke-width="1.6" />
      <ellipse cx="35" cy="35" rx="13.5" ry="4.6" transform="rotate(-22 35 35)" fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" />
      <circle cx="44.5" cy="27.5" r="1.5" fill="{stroke}" />"""
    if index == 1:
        # Isometric wireframe cube + micro sparkle
        return f"""
      <path d="M 35 24.5 L 44.5 29.8 L 44.5 40.2 L 35 45.5 L 25.5 40.2 L 25.5 29.8 Z" fill="none" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round" />
      <path d="M 25.5 29.8 L 35 35 L 44.5 29.8 M 35 35 L 35 45.5" fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
      <circle cx="44.5" cy="25.5" r="1.3" fill="{stroke}" />"""
    # 4-point star + 2 micro stars
    return f"""
      <path d="M 34 25 L 36.2 31.8 L 43 34 L 36.2 36.2 L 34 43 L 31.8 36.2 L 25 34 L 31.8 31.8 Z" fill="none" stroke="{stroke}" stroke-width="1.6" stroke-linejoin="round" />
      <path d="M 43 24.5 L 43.8 26.7 L 46 27.5 L 43.8 28.3 L 43 30.5 L 42.2 28.3 L 40 27.5 L 42.2 26.7 Z" fill="{stroke}" />
      <circle cx="26.5" cy="42.5" r="1.3" fill="{stroke}" />"""


def generate_focus_svg(lang: str, theme_name: str) -> str:
    """Build the 3-column focus areas SVG card strip."""
    t = THEMES[theme_name]
    copy = FOCUS_COPY[lang]
    card_w = 262
    card_h = 146
    xs = [1, 279, 557]

    defs_lines = []
    cards_markup = []
    for idx, x in enumerate(xs):
        fc = t["focus_cards"][idx]
        cc = copy["cards"][idx]
        grad_id = f"focus-bg-{idx}"
        defs_lines.append(
            f'    <linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">\n'
            f'      <stop offset="0%" stop-color="{fc["bg_start"]}" />\n'
            f'      <stop offset="100%" stop-color="{fc["bg_end"]}" />\n'
            f'    </linearGradient>'
        )
        tag_x = card_w - 18 - cc["tag_w"]
        tag_cx = tag_x + cc["tag_w"] / 2
        icon_markup = focus_icon_svg(idx, fc["icon_stroke"])
        cards_markup.append(f"""  <g transform="translate({x}, 1)">
    <rect width="{card_w}" height="{card_h}" rx="16" fill="url(#{grad_id})" stroke="{fc['border']}" stroke-width="1.25" />
    <rect x="18" y="18" width="34" height="34" rx="10" fill="{fc['icon_bg']}" />{icon_markup}
    <rect x="{tag_x}" y="24" width="{cc['tag_w']}" height="20" rx="10" fill="{fc['tag_bg']}" />
    <text x="{tag_cx:.1f}" y="37.5" text-anchor="middle" font-family="{FONT_FAMILY}" font-size="9.5" font-weight="600" letter-spacing="0.8" fill="{fc['tag_ink']}">{cc['tag']}</text>
    <text x="18" y="76" font-family="{FONT_FAMILY}" font-size="14.5" font-weight="700" fill="{t['primary_ink']}">{cc['title']}</text>
    <text x="18" y="100" font-family="{FONT_FAMILY}" font-size="11.5" fill="{t['secondary_ink']}">{cc['line1']}</text>
    <text x="18" y="119" font-family="{FONT_FAMILY}" font-size="11.5" fill="{t['secondary_ink']}">{cc['line2']}</text>
  </g>""")

    defs_block = "\n".join(defs_lines)
    cards_block = "\n".join(cards_markup)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="148" viewBox="0 0 820 148" role="img" aria-label="{copy['aria']}">
  <defs>
{defs_block}
  </defs>
{cards_block}
</svg>
'''


TECH_ITEMS = [
    ("Python", 80, "lavender", "#9B7CC8"),
    ("C#", 56, "blush", "#D67CA8"),
    ("TypeScript", 102, "periwinkle", "#7A92D6"),
    ("Swift", 68, "blush", "#DF8A9C"),
    ("Unity", 68, "lavender", "#9C7DC2"),
    ("QGIS", 68, "periwinkle", "#7BA89C"),
    ("HTML / CSS", 104, "blush", "#D88996"),
    ("Node.js", 84, "lavender", "#80AB8C"),
]


def generate_tech_stack_svg(theme_name: str) -> str:
    """Build a horizontally centered row of pastel tech-stack pills."""
    t = THEMES[theme_name]
    gap = 10
    total_w = sum(w for _, w, _, _ in TECH_ITEMS) + gap * (len(TECH_ITEMS) - 1)
    cursor_x = (820 - total_w) / 2

    pills = []
    for label, width, tone, dot_color in TECH_ITEMS:
        style = t["pills"][tone]
        text_x = cursor_x + 25 + (width - 25 - 10) / 2
        pills.append(
            f'  <g transform="translate({cursor_x:.1f}, 7)">\n'
            f'    <rect width="{width}" height="30" rx="15" fill="{style["bg"]}" stroke="{style["border"]}" stroke-width="1.2" />\n'
            f'    <circle cx="15" cy="15" r="3.5" fill="{dot_color}" />\n'
            f'    <text x="{text_x - cursor_x:.1f}" y="19.2" text-anchor="middle" font-family="{FONT_FAMILY}" font-size="12" font-weight="600" fill="{style["ink"]}">{label}</text>\n'
            f'  </g>'
        )
        cursor_x += width + gap

    pills_block = "\n".join(pills)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="44" viewBox="0 0 820 44" role="img" aria-label="Tech stack: Python, C#, TypeScript, Swift, Unity, QGIS, HTML / CSS, Node.js">
{pills_block}
</svg>
'''


def generate_divider_svg(theme_name: str) -> str:
    """Build a delicate fading starlight hairline divider."""
    t = THEMES[theme_name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="24" viewBox="0 0 820 24" aria-hidden="true">
  <defs>
    <linearGradient id="div-left" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent_start']}" stop-opacity="0" />
      <stop offset="100%" stop-color="{t['accent_start']}" stop-opacity="0.55" />
    </linearGradient>
    <linearGradient id="div-right" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{t['accent_end']}" stop-opacity="0.55" />
      <stop offset="100%" stop-color="{t['accent_end']}" stop-opacity="0" />
    </linearGradient>
  </defs>
  <line x1="40" y1="12" x2="382" y2="12" stroke="url(#div-left)" stroke-width="1.2" stroke-linecap="round" />
  <circle cx="393" cy="12" r="1.4" fill="{t['star_fill']}" opacity="0.7" />
  <path d="M 410 5.5 L 411.7 10.3 L 416.5 12 L 411.7 13.7 L 410 18.5 L 408.3 13.7 L 403.5 12 L 408.3 10.3 Z" fill="{t['star_fill']}" />
  <circle cx="427" cy="12" r="1.4" fill="{t['star_dot']}" opacity="0.7" />
  <line x1="438" y1="12" x2="780" y2="12" stroke="url(#div-right)" stroke-width="1.2" stroke-linecap="round" />
</svg>
'''


def generate_sponsor_svg(lang: str, theme_name: str) -> str:
    """Build the themed GitHub Sponsors CTA button pill."""
    t = THEMES[theme_name]
    s = t["sponsor"]
    if lang == "ja":
        label = "GitHub Sponsors で支援する"
        aria = "GitHub Sponsorsで開発を支援する"
    else:
        label = "Support via GitHub Sponsors"
        aria = "Support my work through GitHub Sponsors"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="272" height="42" viewBox="0 0 272 42" role="img" aria-label="{aria}">
  <defs>
    <linearGradient id="sponsor-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{s['bg_start']}" />
      <stop offset="100%" stop-color="{s['bg_end']}" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="270" height="40" rx="20" fill="url(#sponsor-bg)" stroke="{s['border']}" stroke-width="1.25" />
  <path d="M 28.5 27.2 C 28.5 27.2 22 22.8 22 18.2 C 22 16.1 23.6 14.5 25.6 14.5 C 26.8 14.5 27.9 15.1 28.5 16.1 C 29.1 15.1 30.2 14.5 31.4 14.5 C 33.4 14.5 35 16.1 35 18.2 C 35 22.8 28.5 27.2 28.5 27.2 Z" fill="none" stroke="{s['heart']}" stroke-width="1.6" stroke-linejoin="round" />
  <text x="141" y="25.2" text-anchor="middle" font-family="{FONT_FAMILY}" font-size="12.5" font-weight="600" fill="{s['ink']}">{label}</text>
  <path d="M 244 24 L 250 18 M 245.5 18 L 250 18 L 250 22.5" fill="none" stroke="{s['arrow']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
</svg>
'''


def main() -> None:
    assets_dir = Path("assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    for theme in ("light", "dark"):
        (assets_dir / f"tech-stack-{theme}.svg").write_text(
            generate_tech_stack_svg(theme), encoding="utf-8"
        )
        (assets_dir / f"divider-{theme}.svg").write_text(
            generate_divider_svg(theme), encoding="utf-8"
        )
        for lang in ("ja", "en"):
            (assets_dir / f"focus-{lang}-{theme}.svg").write_text(
                generate_focus_svg(lang, theme), encoding="utf-8"
            )
            (assets_dir / f"sponsor-{lang}-{theme}.svg").write_text(
                generate_sponsor_svg(lang, theme), encoding="utf-8"
            )

    print("Generated all static profile SVGs.")


if __name__ == "__main__":
    main()
