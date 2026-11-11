"""4探針法の理論モデル: 裏面が絶縁(空気)の均一な平板。

表面の点電流源 I が距離 r の表面点に作る電位(鏡像法):
    phi(r) = rho*I/(2*pi) * [ 1/r + 2 * sum_{n>=1} 1/sqrt(r^2 + (2*n*t)^2) ]
級数そのものは発散するが、電位差は収束する。

等間隔 s の4本ピン (位置 0, s, 2s, 3s) について2つの配置を計算する:
    alpha: 電流 = ピン1,4  電圧 = ピン2,3  (Wenner)
    beta : 電流 = ピン1,2  電圧 = ピン3,4  (dipole-dipole)
比 R_alpha / R_beta は抵抗率 rho に依存せず、t/s だけで決まる。

使い方: python3 tools/four_point_model.py [ピン間隔mm ...]
"""
import sys

import numpy as np

N_IMAGES = 200_000


def _g(r, t):
    """phi(r) * 2*pi / (rho*I)。定数項を除き差分でのみ意味を持つ。r, t は同じ単位。"""
    n = np.arange(1, N_IMAGES + 1)
    return 1.0 / r + 2.0 * np.sum(1.0 / np.sqrt(r * r + (2.0 * n * t) ** 2) - 1.0 / (2.0 * n * t))


def transfer_resistance(pos_c1, pos_c2, pos_p1, pos_p2, t):
    """(V_p1 - V_p2) / I を rho=1 で返す [1/長さ]。C1 から流入、C2 から流出。"""
    def phi(p):
        return _g(abs(p - pos_c1), t) - _g(abs(p - pos_c2), t)
    return (phi(pos_p1) - phi(pos_p2)) / (2.0 * np.pi)


def alpha(s, t):
    return transfer_resistance(0, 3 * s, s, 2 * s, t)


def beta(s, t):
    return abs(transfer_resistance(0, s, 2 * s, 3 * s, t))


def main():
    spacings = [float(a) for a in sys.argv[1:]] or [6.0, 8.0, 10.0]
    rho = 20.0  # ohm*m, 半乾燥粘土の仮定値 (未実測)
    thick = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20]
    for s in spacings:
        print(f"\nピン間隔 s = {s:g} mm (プローブ全長 {3*s:g} mm), rho = {rho:g} ohm*m と仮定")
        print(" t[mm]  R_alpha[ohm]  R_beta[ohm]  比a/b   比の変化率[%/mm]")
        rows = []
        for t in thick:
            ra = alpha(s * 1e-3, t * 1e-3) * rho
            rb = beta(s * 1e-3, t * 1e-3) * rho
            rows.append((t, ra, rb, ra / rb))
        for i, (t, ra, rb, q) in enumerate(rows):
            j0, j1 = max(i - 1, 0), min(i + 1, len(rows) - 1)
            slope = (rows[j1][3] - rows[j0][3]) / (rows[j1][0] - rows[j0][0]) / q * 100
            print(f"{t:6.0f}  {ra:12.1f}  {rb:11.1f}  {q:5.3f}  {slope:8.2f}")
    print("\n極限値: 薄板 2*ln2/ln(4/3) = %.3f, 半無限体 3.000" % (2 * np.log(2) / np.log(4 / 3)))


if __name__ == "__main__":
    main()
