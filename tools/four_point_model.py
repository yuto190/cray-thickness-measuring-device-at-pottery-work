"""4探針法の理論モデル: 裏面が絶縁(空気)の均一な平板。

表面の点電流源 I が距離 r の表面点に作る電位(鏡像法):
    phi(r) = rho*I/(2*pi) * [ 1/r + 2 * sum_{n>=1} 1/sqrt(r^2 + (2*n*t)^2) ]
級数そのものは発散するが、電位差は収束する。

4本のピン 1〜4 について2つの配置を計算する:
    alpha: 電流 = ピン1,4  電圧 = ピン2,3
    beta : 電流 = ピン1,2  電圧 = ピン4,3
比 R_alpha / R_beta は抵抗率 rho に依存せず、形状と厚みだけで決まる。

ピンの並べ方:
    直線 (間隔 s)   : 1 2 3 4 の順に一列。比は 4.819 (薄) -> 3.000 (厚)
    長方形 (a x b)  : 周に沿って 1,2,3,4。辺 1-2 と 3-4 が短辺 b、辺 1-4 と 2-3 が長辺 a。
                      比は ln(1+(a/b)^2)/ln(1+(b/a)^2) (薄) から増加する。
                      正方形 (a = b) は対称性で比が常に 1 となり、厚みを判別できない。

使い方:
    python3 tools/four_point_model.py [間隔mm ...]                 直線配置の表
    python3 tools/four_point_model.py --rect 5.08 2.54             長方形配置の表
    python3 tools/four_point_model.py --ratio 4.2 --s 5.08         測った比から厚み (直線)
    python3 tools/four_point_model.py --ratio 8.6 --rect 5.08 2.54 測った比から厚み (長方形)
"""
import sys

import numpy as np

N_IMAGES = 20_000
THICKNESSES = [1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]


def linear(s):
    return [(0.0, 0.0), (s, 0.0), (2 * s, 0.0), (3 * s, 0.0)]


def rectangle(a, b):
    return [(0.0, 0.0), (0.0, b), (a, b), (a, 0.0)]


def _g(r, t):
    """phi(r) * 2*pi / (rho*I)。定数項を除き差分でのみ意味を持つ。r, t は同じ単位。"""
    n = np.arange(1, N_IMAGES + 1)
    return 1.0 / r + 2.0 * np.sum(1.0 / np.sqrt(r * r + (2.0 * n * t) ** 2) - 1.0 / (2.0 * n * t))


def transfer_resistance(c1, c2, p1, p2, t):
    """(V_p1 - V_p2) / I を rho=1 で返す [1/長さ]。C1 から流入、C2 から流出。点は (x, y)。"""
    def dist(u, v):
        return float(np.hypot(u[0] - v[0], u[1] - v[1]))

    def phi(p):
        return _g(dist(p, c1), t) - _g(dist(p, c2), t)

    return (phi(p1) - phi(p2)) / (2.0 * np.pi)


def alpha(pins, t):
    return transfer_resistance(pins[0], pins[3], pins[1], pins[2], t)


def beta(pins, t):
    return transfer_resistance(pins[0], pins[1], pins[3], pins[2], t)


def ratio(pins, t):
    return alpha(pins, t) / beta(pins, t)


def thickness_from_ratio(q, pins):
    """比から厚みを二分法で求める。有効範囲外なら None。単位は pins と同じ。"""
    size = max(np.hypot(p[0] - pins[0][0], p[1] - pins[0][1]) for p in pins)
    lo, hi = 0.02 * size, 10.0 * size
    f_lo, f_hi = ratio(pins, lo) - q, ratio(pins, hi) - q
    if f_lo * f_hi > 0:
        return None
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if (ratio(pins, mid) - q) * f_lo > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def print_table(name, pins_mm, rho=20.0):
    pins = [(x * 1e-3, y * 1e-3) for x, y in pins_mm]
    print(f"\n{name}, rho = {rho:g} ohm*m と仮定 (未実測)")
    print(" t[mm]  R_alpha[ohm]  R_beta[ohm]   比a/b   比の変化率[%/mm]")
    for t in THICKNESSES:
        ra, rb = alpha(pins, t * 1e-3) * rho, beta(pins, t * 1e-3) * rho
        slope = (ratio(pins, (t + 0.05) * 1e-3) - ratio(pins, (t - 0.05) * 1e-3)) / 0.1 / (ra / rb) * 100
        print(f"{t:6g}  {ra:12.1f}  {rb:11.1f}  {ra / rb:6.3f}  {slope:8.2f}")


def main():
    args = sys.argv[1:]
    rect = None
    if "--rect" in args:
        i = args.index("--rect")
        rect = (float(args[i + 1]), float(args[i + 2]))
    if "--ratio" in args:
        q = float(args[args.index("--ratio") + 1])
        pins = rectangle(*rect) if rect else linear(float(args[args.index("--s") + 1]))
        t = thickness_from_ratio(q, pins)
        print("範囲外 (この配置で取りうる比ではない)" if t is None else f"厚み = {t:.2f} mm")
        return
    if rect:
        print_table(f"長方形 {rect[0]:g} x {rect[1]:g} mm", rectangle(*rect))
        return
    for s in [float(a) for a in args] or [2.54, 5.08]:
        print_table(f"直線 間隔 s = {s:g} mm (全長 {3 * s:g} mm)", linear(s))


if __name__ == "__main__":
    main()
