import urllib.request
import re
from pathlib import Path

username = "r-fallingstar"
url = f"https://github.com/users/{username}/contributions"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode("utf-8")

cells = dict(re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[^"]+)"', html))
tips = dict(re.findall(r'for="(contribution-day-component-[^"]+)"[^>]*>([^<]+)</tool-tip>', html))

records = []
for date_str, cid in cells.items():
    tip = tips.get(cid, "")
    cnt = 0
    m = re.search(r'(\d+)\s+contribution', tip)
    if m:
        cnt = int(m.group(1))
    records.append((date_str, cnt))

records.sort(key=lambda x: x[0])

total_contributions = sum(r[1] for r in records)

longest = 0
cur_temp = 0
for d, cnt in records:
    if cnt > 0:
        cur_temp += 1
        longest = max(longest, cur_temp)
    else:
        cur_temp = 0

current_streak = 0
for d, cnt in reversed(records):
    if cnt > 0:
        current_streak += 1
    elif current_streak == 0:
        continue
    else:
        break

weekly = []
for i in range(0, len(records), 7):
    chunk = records[i:i+7]
    weekly.append(sum(c for _, c in chunk))

graph_x = 240
graph_y = 150
graph_w = 480
graph_h = 60
max_val = max(max(weekly), 1)

points = []
for i, val in enumerate(weekly):
    x = graph_x + (i / (len(weekly) - 1)) * graph_w
    y = graph_y + graph_h - (val / max_val) * (graph_h - 10)
    points.append((x, y))

path_d = f"M {points[0][0]} {graph_y + graph_h} L {points[0][0]} {points[0][1]}"
for i in range(len(points) - 1):
    p0 = points[i]
    p1 = points[i+1]
    mid_x = (p0[0] + p1[0]) / 2
    path_d += f" Q {p0[0]} {p0[1]}, {mid_x} {(p0[1] + p1[1]) / 2} T {p1[0]} {p1[1]}"
path_fill = path_d + f" L {points[-1][0]} {graph_y + graph_h} Z"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="260" viewBox="0 0 760 260" role="img" aria-label="開発アクティビティ統計">
  <defs>
    <linearGradient id="card-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FCF9FE" />
      <stop offset="100%" stop-color="#FBF7FC" />
    </linearGradient>
    <linearGradient id="wave-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#DDA9D5" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#DDA9D5" stop-opacity="0.05" />
    </linearGradient>
    <linearGradient id="ring-grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#E8A7C2" />
      <stop offset="100%" stop-color="#DDA9D5" />
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="758" height="258" rx="16" fill="url(#card-bg)" stroke="#EADCF0" stroke-width="1.5" />

  <g transform="translate(130, 60)" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif">
    <text y="-8" font-size="28" font-weight="bold" fill="#5C4266">{total_contributions}</text>
    <text y="16" font-size="12" fill="#8A6894" font-weight="500">年間コントリビューション</text>
    <text y="32" font-size="10" fill="#9C7EA6">過去1年間の活動合計</text>
  </g>

  <line x1="260" y1="20" x2="260" y2="105" stroke="#EADCF0" stroke-width="1" />

  <g transform="translate(380, 58)" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif">
    <circle cx="0" cy="-6" r="32" fill="none" stroke="url(#ring-grad)" stroke-width="3.5" />
    <path d="M 0 -43 Q 4 -36 0 -32 Q -4 -36 0 -43 Z" fill="#ECA1C4" />
    <text y="3" font-size="26" font-weight="bold" fill="#5C4266">{current_streak}日</text>
    <text y="24" font-size="12" fill="#8A6894" font-weight="600">現在の継続日数</text>
  </g>

  <line x1="500" y1="20" x2="500" y2="105" stroke="#EADCF0" stroke-width="1" />

  <g transform="translate(630, 60)" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif">
    <text y="-8" font-size="28" font-weight="bold" fill="#5C4266">{longest}日</text>
    <text y="16" font-size="12" fill="#8A6894" font-weight="500">最長継続日数</text>
    <text y="32" font-size="10" fill="#9C7EA6">自己ベスト記録</text>
  </g>

  <line x1="30" y1="120" x2="730" y2="120" stroke="#F0E3F5" stroke-width="1" />

  <g transform="translate(40, 155)" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif" font-size="12" fill="#64516E">
    <g transform="translate(0, 0)">
      <circle cx="6" cy="6" r="4" fill="#E8A7C2" />
      <text x="18" y="10" font-weight="500">開発活動：アクティブ</text>
    </g>
    <g transform="translate(0, 24)">
      <circle cx="6" cy="6" r="4" fill="#DDA9D5" />
      <text x="18" y="10">公開リポジトリ：1 件</text>
    </g>
    <g transform="translate(0, 48)">
      <circle cx="6" cy="6" r="4" fill="#B3CDE0" />
      <text x="18" y="10">拠点：福井県, 日本 🇯🇵</text>
    </g>
    <g transform="translate(0, 72)">
      <circle cx="6" cy="6" r="4" fill="#C1E1C1" />
      <text x="18" y="10">GitHub歴：3年目</text>
    </g>
  </g>

  <text x="240" y="142" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif" font-size="11" font-weight="600" fill="#8A6894">過去1年間のアクティビティ推移</text>
  
  <path d="{path_fill}" fill="url(#wave-grad)" />
  <path d="{path_d}" fill="none" stroke="#B87CAE" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />

  <line x1="{graph_x}" y1="{graph_y + graph_h}" x2="{graph_x + graph_w}" y2="{graph_y + graph_h}" stroke="#EADCF0" stroke-width="1" />

  <g font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif" font-size="10" fill="#9C7EA6" text-anchor="middle">
    <text x="240" y="{graph_y + graph_h + 16}">11月</text>
    <text x="320" y="{graph_y + graph_h + 16}">1月</text>
    <text x="400" y="{graph_y + graph_h + 16}">3月</text>
    <text x="480" y="{graph_y + graph_h + 16}">5月</text>
    <text x="560" y="{graph_y + graph_h + 16}">7月</text>
    <text x="640" y="{graph_y + graph_h + 16}">9月</text>
    <text x="715" y="{graph_y + graph_h + 16}">現在</text>
  </g>
</svg>'''

out_path = Path("assets/activity-card-ja.svg")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(svg, encoding="utf-8")
print(f"Generated {out_path}")

