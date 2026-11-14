"""Builds dist/space-strafe.svg from a GitHub user's real contribution calendar."""
import json, os, random, sys, urllib.request

USER = os.environ.get("GH_USER") or sys.exit("GH_USER not set")
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch():
    mock = os.environ.get("MOCK_JSON")
    if mock:
        return json.load(open(mock))
    q = ("query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{"
         "weeks{contributionDays{weekday contributionLevel}}}}}}")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"u": USER}}).encode(),
        headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "User-Agent": "space-strafe"},
    )
    return json.load(urllib.request.urlopen(req, timeout=30))


data = fetch()
if data.get("errors") or not data.get("data", {}).get("user"):
    sys.exit("GitHub API error: " + json.dumps(data)[:500])
weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
COLS, ROWS = len(weeks), 7
lv = [[0] * ROWS for _ in range(COLS)]
for c, w in enumerate(weeks):
    for d in w["contributionDays"]:
        lv[c][d["weekday"]] = LEVELS.get(d["contributionLevel"], 0)

random.seed(7)
S, G = 11, 3
STEP = S + G; GX, GY = 24, 26; T = 18.0; RUN = 0.9
W = GX * 2 + COLS * STEP - G; GRID_H = ROWS * STEP - G; SHIP_Y = GY + GRID_H + 26; H = SHIP_Y + 30
PAL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">']
o.append(f'''<style>
.c{{transform-box:fill-box;transform-origin:center;animation:hit {T}s linear infinite}}
.l{{opacity:0;animation:zap {T}s linear infinite}}
.s{{animation:tw 3s ease-in-out infinite}}
#ship{{animation:fly {T}s linear infinite}}
.fl{{animation:fl .12s linear infinite alternate}}
@keyframes hit{{0%,49.9%{{opacity:1;transform:scale(1)}}50%{{opacity:1;fill:#fff;transform:scale(1.7)}}52%,88%{{opacity:0;transform:scale(.2)}}96%,100%{{opacity:1;transform:scale(1)}}}}
@keyframes zap{{0%,49.6%{{opacity:0}}49.8%,50.6%{{opacity:1}}51.4%,100%{{opacity:0}}}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
@keyframes fly{{0%{{transform:translateX(0);opacity:1}}{RUN*100}%{{transform:translateX({COLS*STEP}px);opacity:1}}{RUN*100+3}%{{transform:translateX({COLS*STEP+40}px);opacity:0}}{RUN*100+3.1}%{{transform:translateX(-40px);opacity:0}}100%{{transform:translateX(0);opacity:1}}}}
@keyframes fl{{from{{transform:scaleY(.6)}}to{{transform:scaleY(1.2)}}}}
</style>''')
o.append(f'<rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>')
for _ in range(60):
    x = random.uniform(4, W - 4); y = random.uniform(4, H - 4); r = random.choice([.5, .7, 1, 1.2])
    o.append(f'<circle class="s" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#c9d1d9" style="animation-delay:-{random.uniform(0,3):.2f}s"/>')
for c in range(COLS):
    x = GX + c * STEP; tc = (c + .5) / COLS * RUN * T; top = None
    for r in range(ROWS):
        y = GY + r * STEP; v = lv[c][r]
        o.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S}" rx="2" fill="{PAL[0]}"/>')
        if v:
            if top is None: top = y
            d = tc + (ROWS - 1 - r) * 0.035 - 0.5 * T
            o.append(f'<rect class="c" x="{x}" y="{y}" width="{S}" height="{S}" rx="2" fill="{PAL[v]}" style="animation-delay:{d:.3f}s"/>')
    if top is not None:
        lx = x + S / 2
        o.append(f'<line class="l" x1="{lx}" y1="{SHIP_Y-10}" x2="{lx}" y2="{top}" stroke="#ff4dd8" stroke-width="2" stroke-linecap="round" style="animation-delay:{tc-0.5*T:.3f}s"/>')
o.append(f'''<g id="ship"><g transform="translate({GX},{SHIP_Y})">
<path class="fl" d="M-3 9 L0 19 L3 9Z" fill="#ffb347" style="transform-box:fill-box;transform-origin:top"/>
<path d="M0 -11 L4 2 L13 8 L13 11 L4 8 L0 10 L-4 8 L-13 11 L-13 8 L-4 2Z" fill="#58e6ff" stroke="#0d1117" stroke-width=".6"/>
<path d="M0 -6 L2 2 L-2 2Z" fill="#0d1117"/>
<rect x="-13.6" y="3" width="1.6" height="7" fill="#ff4dd8"/><rect x="12" y="3" width="1.6" height="7" fill="#ff4dd8"/>
</g></g>''')
o.append('</svg>')
os.makedirs("dist", exist_ok=True)
open("dist/space-strafe.svg", "w").write("\n".join(o))
print(f"wrote dist/space-strafe.svg ({COLS} weeks)")
