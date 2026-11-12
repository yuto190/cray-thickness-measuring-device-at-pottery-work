"""実験1: 4探針法で R_alpha / R_beta を測る (XIAO ESP32C3 + ADS1115, MicroPython)

配線は docs/experiment1.md を参照。探針の並べ方は直線・長方形のどちらでも同じプログラムで測れる
(長方形では周に沿って 1,2,3,4 と番号を振り、辺 1-2 を短辺にする)。マルチプレクサは使わず、
各ピンを「直列抵抗 RS 経由の GPIO」と「ADS1115 の入力」の両方につなぐ。
  - 電流を流すピン : GPIO を出力 (H または L)
  - 電圧を測るピン : GPIO を入力 (ハイインピーダンス)
電流は、吸い込み側ピンの電圧 / RS で求める。

注意: 実機での動作は未確認。
"""
import struct
import time

from machine import I2C, Pin

RS = 10_000.0          # 各ピンの直列抵抗 [ohm]。テスターで実測した値に書き換えると精度が上がる
ADS_ADDR = 0x48
I2C_SDA, I2C_SCL = 6, 7                      # XIAO ESP32C3 の D4, D5
PIN_GPIO = {1: 3, 2: 4, 3: 5, 4: 10}         # 探針番号 -> GPIO (D1, D2, D3, D10)
AIN_OF_PIN = {1: 0, 2: 1, 3: 3, 4: 2}        # 探針番号 -> ADS1115 の AIN 番号

MUX_SINGLE = {0: 0b100, 1: 0b101, 2: 0b110, 3: 0b111}
CONFIGS = {
    # 名前: (電流ピンA, 電流ピンB, 電圧測定のMUX設定)。A->B に流したとき電圧が正になる向き
    "alpha": (1, 4, 0b010),   # 電流 1-4, 電圧 AIN1 - AIN3 = 探針2 - 探針3
    "beta": (1, 2, 0b011),    # 電流 1-2, 電圧 AIN2 - AIN3 = 探針4 - 探針3
}

# (PGA設定値, フルスケール[V])。レンジが狭いほど分解能は上がるが入力インピーダンスは下がる
# (+-4.096 V: 約15 Mohm, +-1.024 V: 約2.4 Mohm)。+-0.512 V 以下は 710 kohm と低いので使わない
PGA_RANGES = ((0b001, 4.096), (0b010, 2.048), (0b011, 1.024))
PGA_WIDE = PGA_RANGES[0]
SETTLE_MS = 20                # 極性を切り替えてから測るまでの待ち時間
N_VOLT = 16                   # 1極性あたりの電圧サンプル数
N_CYCLES = 4                  # 極性反転の繰り返し回数
MIN_CURRENT = 5e-6            # これ未満なら接触不良とみなす [A]

i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)


def ads_read(mux, pga=PGA_WIDE):
    """単発変換して電圧 [V] を返す。"""
    cfg = 0x8000 | (mux << 12) | (pga[0] << 9) | 0x0100 | (0b111 << 5) | 0b00011
    i2c.writeto_mem(ADS_ADDR, 0x01, struct.pack(">H", cfg))
    time.sleep_ms(2)          # 860 SPS -> 変換時間 約1.2 ms
    return struct.unpack(">h", i2c.readfrom_mem(ADS_ADDR, 0x00, 2))[0] * pga[1] / 32768


def pick_range(volts):
    """信号がフルスケールの 2/3 以下に収まる最も狭いレンジを選ぶ。"""
    best = PGA_WIDE
    for pga in PGA_RANGES:
        if abs(volts) < pga[1] * 2 / 3:
            best = pga
    return best


def all_off():
    for gpio in PIN_GPIO.values():
        Pin(gpio, Pin.IN)


def drive(source, sink):
    all_off()
    Pin(PIN_GPIO[source], Pin.OUT, value=1)
    Pin(PIN_GPIO[sink], Pin.OUT, value=0)


def measure(name):
    """伝達抵抗 [ohm] と電流 [A] を返す。接触不良なら (None, 電流)。"""
    pin_a, pin_b, vmux = CONFIGS[name]
    r_sum = i_sum = 0.0
    n = 0
    for _ in range(N_CYCLES):
        for source, sink, sign in ((pin_a, pin_b, 1.0), (pin_b, pin_a, -1.0)):
            drive(source, sink)
            time.sleep_ms(SETTLE_MS)
            sense = MUX_SINGLE[AIN_OF_PIN[sink]]
            i_before = ads_read(sense)
            pga = pick_range(ads_read(vmux))
            v = sum(ads_read(vmux, pga) for _ in range(N_VOLT)) / N_VOLT
            i_after = ads_read(sense)
            current = (i_before + i_after) / 2 / RS
            if current < MIN_CURRENT:
                all_off()
                return None, current
            r_sum += sign * v / current
            i_sum += current
            n += 1
    all_off()
    return r_sum / n, i_sum / n


def main():
    all_off()
    found = i2c.scan()
    print("# I2C devices:", [hex(a) for a in found])
    if ADS_ADDR not in found:
        print("# ADS1115 が 0x%02x に見つからない。配線とアドレス設定を確認" % ADS_ADDR)
        return
    print("# label,R_alpha_ohm,R_beta_ohm,ratio,I_alpha_uA,I_beta_uA")
    while True:
        label = input("ラベル(例: t5_s2.54)を入力して Enter: ")
        for _ in range(3):
            ra, ia = measure("alpha")
            rb, ib = measure("beta")
            if ra is None or rb is None or rb <= 0:
                print("# 接触不良または異常値: I_alpha=%.1f uA, I_beta=%.1f uA" % (ia * 1e6, ib * 1e6))
                continue
            print("%s,%.1f,%.1f,%.4f,%.1f,%.1f" % (label, ra, rb, ra / rb, ia * 1e6, ib * 1e6))


main()
