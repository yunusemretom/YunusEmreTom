#!/usr/bin/env python3
"""Render the project cards shown in README.md as animated SVGs.

GitHub strips CSS from READMEs, so a table border can't be styled. Drawing the
cards as SVG images is the only way to get a colored, animated border, and it
keeps the data (stars, language) live because the workflow re-runs this.
"""
import json
import os
import textwrap
import urllib.request

OWNER = "yunusemretom"
REPOS = [
    ("Yer-Istasyonu", "Open-source ground control station for UAV, rocket and satellite teams."),
    ("TOM_AI", "AI-powered voice assistant with Turkish language support."),
    ("DogFight", "ROS 2 + PX4 visual target tracking and offboard drone control."),
    ("Celik_Kubbe", "Vision-based air defense system built for Team Pars."),
]

W, H = 420, 132
OUT = os.environ.get("OUT_DIR", "dist")


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-cards"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(name, desc, stars, lang):
    lines = textwrap.wrap(desc, width=58)[:2]
    body = "".join(
        f'<text class="desc" x="20" y="{62 + i * 18}">{esc(l)}</text>' for i, l in enumerate(lines)
    )
    meta = f"{stars}" + (f"   ·   {lang}" if lang else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)}: {esc(desc)}">
  <style>
    .bg     {{ fill: #0d1117; }}
    .edge   {{ stroke: #30363d; }}
    .title  {{ fill: #3fb950; font: 700 16px ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .desc   {{ fill: #8b949e; font: 400 12.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}
    .meta   {{ fill: #6e7681; font: 400 12px ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .star   {{ fill: #d29922; }}
    @media (prefers-color-scheme: light) {{
      .bg   {{ fill: #ffffff; }}
      .edge {{ stroke: #d0d7de; }}
      .title{{ fill: #1a7f37; }}
      .desc {{ fill: #57606a; }}
      .meta {{ fill: #6e7781; }}
    }}
  </style>

  <defs>
    <linearGradient id="run" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#3fb950" stop-opacity="0"/>
      <stop offset="50%"  stop-color="#3fb950" stop-opacity="1"/>
      <stop offset="100%" stop-color="#2f81f7" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect class="bg edge" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" stroke-width="1.5"/>

  <!-- travelling highlight along the border -->
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="none"
        stroke="url(#run)" stroke-width="2" stroke-linecap="round"
        pathLength="1000" stroke-dasharray="180 820">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="4s" repeatCount="indefinite"/>
  </rect>

  <text class="title" x="20" y="34">{esc(name)}</text>
  {body}
  <path class="star" d="M8 0.6 9.9 5 14.6 5.4 11 8.5 12.1 13.1 8 10.6 3.9 13.1 5 8.5 1.4 5.4 6.1 5Z"
        transform="translate(20 {H - 32}) scale(0.72)"/>
  <text class="meta" x="{20 + 16}" y="{H - 20}">{esc(meta)}</text>
</svg>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, desc in REPOS:
        data = api(f"/repos/{OWNER}/{name}")
        svg = card(name, desc, data.get("stargazers_count", 0), data.get("language") or "")
        path = os.path.join(OUT, f"card-{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}  (stars={data.get('stargazers_count')}, lang={data.get('language')})")


if __name__ == "__main__":
    main()
