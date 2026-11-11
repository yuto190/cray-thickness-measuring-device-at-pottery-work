# cray-thickness-measuring-device-at-pottery-work

陶芸の高台削りで、半乾燥状態の粘土の厚みを外側から測るための自作測定器。

作品の内側には何も入れない方式に限定し、4探針抵抗法を主軸、超音波を並行評価として検討中。

- [設計書 (コンセプト・仕様・部品・費用)](docs/design.md)
- [実験 1 の配線と手順](docs/experiment1.md)
- [実験 1 の測定プログラム](firmware/experiment1/main.py) — XIAO ESP32C3 + ADS1115, MicroPython
- [4探針法の理論モデル](tools/four_point_model.py) — `python3 tools/four_point_model.py 3 6` (要 numpy)
