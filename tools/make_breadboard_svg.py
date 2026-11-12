"""実験1のブレッドボード組立図 (docs/img/experiment1_breadboard.svg) を生成する。

使い方: python3 tools/make_breadboard_svg.py
"""
import os

P = 24
X0, Y0 = 190, 170
COL = {c: i for i, c in enumerate("abcde")}
COL.update({c: i + 7 for i, c in enumerate("fghij")})
W, H = 930, 1110

ORANGE, GREEN, BLUE, PURPLE = "#e8590c", "#2f9e44", "#1c7ed6", "#9c36b5"
RED, BLACK, YELLOW, WHITE = "#e03131", "#222222", "#f2c400", "#ffffff"
PROBE_COLOR = {1: ORANGE, 2: GREEN, 3: BLUE, 4: PURPLE}

out = []


def x(col):
    return X0 + COL[col] * P


def y(row):
    return Y0 + (row - 1) * P


def add(s):
    out.append(s)


def text(px, py, s, size=12, anchor="middle", fill="#222", weight="normal"):
    add(f'<text x="{px}" y="{py}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
        f'font-weight="{weight}">{s}</text>')


def wire(points, color, width=5):
    d = "M" + " L".join(f"{px},{py}" for px, py in points)
    outline = "#555" if color in (WHITE, YELLOW) else "#00000055"
    add(f'<path d="{d}" fill="none" stroke="{outline}" stroke-width="{width + 2}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>')


def plug(col, row, color):
    add(f'<circle cx="{x(col)}" cy="{y(row)}" r="5.5" fill="{color}" stroke="#222" stroke-width="1.2"/>')


def label(px, py, s, color, w=None, size=12):
    w = w or (len(s) * size * 0.62 + 14)
    dark = color not in (WHITE, YELLOW)
    add(f'<rect x="{px - w / 2}" y="{py - 11}" width="{w}" height="22" rx="5" fill="{color}" '
        f'stroke="#444" stroke-width="1"/>')
    text(px, py + 4, s, size=size, fill="#fff" if dark else "#222", weight="bold")


def resistor(row):
    xa, xb, yy = x("e"), x("f"), y(row)
    add(f'<line x1="{xa}" y1="{yy}" x2="{xb}" y2="{yy}" stroke="#888" stroke-width="2.5"/>')
    add(f'<rect x="{xa + 16}" y="{yy - 6}" width="{xb - xa - 32}" height="12" rx="5" fill="#d9b382" stroke="#7a5c33"/>')
    for i, c in enumerate(("#6b3a12", "#111", "#111", "#e8590c")):
        add(f'<rect x="{xa + 22 + i * 8}" y="{yy - 6}" width="3.5" height="12" fill="{c}"/>')
    for xx in (xa, xb):
        add(f'<circle cx="{xx}" cy="{yy}" r="4" fill="#bbb" stroke="#444"/>')


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="\'Noto Sans JP\', \'Hiragino Sans\', \'Yu Gothic\', Meiryo, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(W / 2, 34, "実験1 ブレッドボード組立図 (XIAO ESP32C3 + Grove ADS1115)", size=19, weight="bold")
text(W / 2, 56, "上から見た図。同じ行の a〜e、f〜j はそれぞれ内部でつながっている。両端の電源ライン(＋／−)は使わない。",
     size=12, fill="#555")

# --- ブレッドボード ---
bx0, bx1 = X0 - 3.75 * P, X0 + 14.75 * P
by0, by1 = Y0 - 1.25 * P, y(30) + 1.25 * P
add(f'<rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" rx="8" fill="#f6f3ea" stroke="#b9b29e"/>')
for row in range(1, 31):
    for cols in ("ae", "fj"):
        add(f'<line x1="{x(cols[0])}" y1="{y(row)}" x2="{x(cols[1])}" y2="{y(row)}" stroke="#e2dccb" stroke-width="9" '
            f'stroke-linecap="round"/>')
    for c in COL:
        add(f'<circle cx="{x(c)}" cy="{y(row)}" r="3" fill="#8d8878"/>')
    for idx in (-3, -2, 13, 14):
        add(f'<circle cx="{X0 + idx * P}" cy="{y(row)}" r="3" fill="#cfc9b8"/>')
    if row == 1 or row % 5 == 0:
        text(X0 - P, y(row) + 4, row, size=10, fill="#777")
        text(X0 + 12 * P, y(row) + 4, row, size=10, fill="#777")
for c in COL:
    text(x(c), y(30) + 21, c, size=11, fill="#777")
for idx, s, col in ((-3, "＋", "#e03131"), (-2, "−", "#1c7ed6"), (13, "＋", "#e03131"), (14, "−", "#1c7ed6")):
    text(X0 + idx * P, y(30) + 21, s, size=11, fill=col)

# --- XIAO ESP32C3 (行1〜7、ピンは e 列と i 列) ---
xl, xr = x("e") - 11, x("i") + 11
add(f'<rect x="{xl}" y="{y(1) - 20}" width="{xr - xl}" height="{y(7) - y(1) + 34}" rx="6" fill="#26262c" stroke="#000"/>')
ucx = (xl + xr) / 2
add(f'<rect x="{ucx - 30}" y="{y(1) - 40}" width="60" height="30" rx="5" fill="#b8bcc4" stroke="#555"/>')
text(ucx, y(1) - 46, "USB-C → PC", size=11, fill="#444")
left = ["D0", "D1", "D2", "D3", "D4 SDA", "D5 SCL", "D6"]
right = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
for i in range(7):
    for col, names, anchor, dx in (("e", left, "start", 10), ("i", right, "end", -10)):
        add(f'<circle cx="{x(col)}" cy="{y(i + 1)}" r="4.5" fill="#d4af37" stroke="#7a6520"/>')
        text(x(col) + dx, y(i + 1) + 4, names[i], size=11, anchor=anchor, fill="#fff")
text(ucx, y(4) - 2, "XIAO", size=13, fill="#9aa0aa", weight="bold")
text(ucx, y(4) + 14, "ESP32C3", size=11, fill="#9aa0aa")

# --- 抵抗 10kΩ ×4 (e-f 間、中央の溝をまたぐ) ---
NODE_ROW = {3: 20, 2: 22, 1: 24, 4: 26}          # 探針番号 -> 行
for row in NODE_ROW.values():
    resistor(row)
text((x("e") + x("f")) / 2, y(19) + 2, "10kΩ ×4", size=11, fill="#7a5c33", weight="bold")

# --- XIAO -> 抵抗の左側 (ジャンパ線) ---
for probe, src_row, lane in ((3, 4, 82), (2, 3, 64), (1, 2, 46)):
    c = PROBE_COLOR[probe]
    wire([(x("a"), y(src_row)), (lane, y(src_row)), (lane, y(NODE_ROW[probe])), (x("a"), y(NODE_ROW[probe]))], c)
    plug("a", src_row, c)
    plug("a", NODE_ROW[probe], c)
c = PROBE_COLOR[4]
wire([(x("j"), y(4)), (x("j"), y(8.5)), (x("b"), y(8.5)), (x("b"), y(26))], c)
plug("j", 4, c)
plug("b", 26, c)

# --- ADS1115 モジュール ---
mx, my, mw, mh = 664, y(2) - 46, 214, 184
add(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="8" fill="#1e4a8c" stroke="#0d2748"/>')
text(mx + mw / 2 + 14, my + 24, "Grove ADS1115", size=13, fill="#fff", weight="bold")
text(mx + mw / 2 + 14, my + 42, "16bit ADC", size=11, fill="#cfe0ff")
add(f'<rect x="{mx - 12}" y="{y(2) - 14}" width="30" height="{3 * P + 28}" rx="3" fill="#f1f1f1" stroke="#666"/>')
for i, name in enumerate(("GND", "VCC", "SDA", "SCL")):
    text(mx + 24, y(2 + i) + 4, name, size=10, anchor="start", fill="#fff")
text(mx + 3, y(2) - 20, "Grove (I2C)", size=10, fill="#fff", anchor="start")
add(f'<rect x="{mx + mw - 18}" y="{y(2) - 6}" width="30" height="{2 * P + 12}" rx="3" fill="#f1f1f1" stroke="#666"/>')
text(mx + mw - 24, y(3) + 4, "不使用", size=10, anchor="end", fill="#cfe0ff")
TERM = {name: mx + 32 + i * 30 for i, name in enumerate(("VCC", "GND", "A0", "A1", "A2", "A3"))}
ty = my + mh - 10
add(f'<rect x="{mx + 14}" y="{ty}" width="186" height="32" rx="3" fill="#3fa35b" stroke="#1d5c30"/>')
for name, tx in TERM.items():
    add(f'<circle cx="{tx}" cy="{ty + 16}" r="8" fill="#c9ced6" stroke="#555"/>')
    add(f'<line x1="{tx - 5}" y1="{ty + 16}" x2="{tx + 5}" y2="{ty + 16}" stroke="#555" stroke-width="2"/>')
    text(tx, ty - 6, name, size=10, fill="#fff")
text(mx + mw / 2, my - 10, "下側がネジ端子台(VCC・GND は何もつながない)", size=11, fill="#444")

# --- I2C (Grove - ジャンパケーブル) ---
wire([(x("j"), y(2)), (mx - 4, y(2))], BLACK)
plug("j", 2, BLACK)
wire([(x("j"), y(3)), (mx - 4, y(3))], RED)
plug("j", 3, RED)
text((x("j") + mx) / 2 + 30, y(2) - 8, "黒 GND", size=10, fill="#222")
text((x("j") + mx) / 2 + 30, y(3) - 8, "赤 3V3", size=10, fill="#b02020")
wire([(mx - 4, y(4)), (mx - 34, y(4))], WHITE)
label(mx - 66, y(4), "白 → D4", WHITE, w=64, size=11)
wire([(mx - 4, y(5)), (mx - 34, y(5))], YELLOW)
label(mx - 66, y(5), "黄 → D5", YELLOW, w=64, size=11)
wire([(x("d"), y(5)), (x("d"), 112)], WHITE)
plug("d", 5, WHITE)
label(x("d") + 22, 100, "白 SDA (ADSへ)", WHITE, w=112, size=11)
wire([(x("c"), y(6)), (x("c"), 86)], YELLOW)
plug("c", 6, YELLOW)
label(x("c") - 34, 76, "黄 SCL (ADSへ)", YELLOW, w=112, size=11)

# --- ノード -> ADS 端子台 ---
for probe, term in ((3, "A0"), (2, "A1"), (1, "A2"), (4, "A3")):
    c, row = PROBE_COLOR[probe], NODE_ROW[probe]
    wire([(x("j"), y(row)), (TERM[term], y(row)), (TERM[term], ty + 26)], c)
    plug("j", row, c)

# --- ノード -> 電極 (リード線) ---
LEAD = {3: ("g", -12, 200), 2: ("g", 12, 315), 1: ("h", 12, 430), 4: ("i", 12, 545)}
for probe, (col, dx, endx) in LEAD.items():
    c, row = PROBE_COLOR[probe], NODE_ROW[probe]
    lane = x(col) + dx
    wire([(x(col), y(row)), (lane, y(row) + 12), (lane, by1 + 6), (endx, by1 + 52), (endx, by1 + 62)], c)
    plug(col, row, c)
    label(endx, by1 + 76, f"電極の探針{probe}へ", c, w=104, size=11)

# --- 電極の説明 ---
ex, ey = 610, 806
add(f'<rect x="{ex}" y="{ey}" width="300" height="250" rx="8" fill="#fafafa" stroke="#bbb"/>')
text(ex + 150, ey + 24, "電極(ピンヘッダ)の番号", size=13, weight="bold")
text(ex + 16, ey + 50, "直線配置: 端から 1, 2, 3, 4", size=12, anchor="start")
for i in range(4):
    cx = ex + 60 + i * 44
    add(f'<circle cx="{cx}" cy="{ey + 80}" r="11" fill="{PROBE_COLOR[i + 1]}" stroke="#222"/>')
    text(cx, ey + 84, i + 1, size=12, fill="#fff", weight="bold")
add(f'<rect x="{ex + 38}" y="{ey + 64}" width="176" height="32" rx="4" fill="none" stroke="#333" stroke-width="1.5"/>')
text(ex + 16, ey + 126, "長方形配置: 周に沿って 1, 2, 3, 4", size=12, anchor="start")
text(ex + 16, ey + 143, "(辺 1-2 が短辺、辺 1-4 が長辺)", size=11, anchor="start", fill="#555")
for probe, (cx, cy) in {2: (0, 0), 3: (88, 0), 1: (0, 44), 4: (88, 44)}.items():
    add(f'<circle cx="{ex + 60 + cx}" cy="{ey + 174 + cy}" r="11" fill="{PROBE_COLOR[probe]}" stroke="#222"/>')
    text(ex + 60 + cx, ey + 178 + cy, probe, size=12, fill="#fff", weight="bold")
add(f'<circle cx="{ex + 104}" cy="{ey + 174}" r="5" fill="#ccc" stroke="#888"/>')
add(f'<circle cx="{ex + 104}" cy="{ey + 218}" r="5" fill="#ccc" stroke="#888"/>')
add(f'<rect x="{ex + 38}" y="{ey + 156}" width="132" height="80" rx="4" fill="none" stroke="#333" stroke-width="1.5"/>')
text(ex + 184, ey + 192, "中央の2本は", size=11, anchor="start", fill="#555")
text(ex + 184, ey + 208, "使わない", size=11, anchor="start", fill="#555")

# --- 色の対応 ---
lx, ly = 600, 420
add(f'<rect x="{lx}" y="{ly}" width="118" height="180" rx="8" fill="#fafafa" stroke="#bbb"/>')
text(lx + 59, ly + 22, "色の対応", size=12, weight="bold")
for i, (probe, pin, term) in enumerate(((1, "D1", "A2"), (2, "D2", "A1"), (3, "D3", "A0"), (4, "D10", "A3"))):
    yy = ly + 46 + i * 34
    add(f'<rect x="{lx + 10}" y="{yy - 10}" width="14" height="14" rx="3" fill="{PROBE_COLOR[probe]}"/>')
    text(lx + 30, yy + 2, f"探針{probe}", size=12, anchor="start", weight="bold")
    text(lx + 30, yy + 17, f"{pin} / {term}", size=11, anchor="start", fill="#555")

add("</svg>")
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "img", "experiment1_breadboard.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("wrote", os.path.normpath(path))
