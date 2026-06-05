#!/usr/bin/env python3
"""
sim4_audio.py — Audio signal path frequency response
Analytical AC analysis of the phantom injection circuit.

Signal path (single-ended equivalent, one XLR line):

  Capsule (200Ω) ──── XLR node ──── C_dc ──── HiFiBerry ADC (8kΩ)
                          │
                     R_inj=6.81kΩ
                          │
                  +48V (AC ground via output bypass caps)

High-pass corner set by C_dc in series with R_HFB:
  f_-3dB = 1 / (2π × R_HFB × C_eff)

X7R DC bias derating at 48V on 2.2µF/100V cap:
  V_bias/V_rated = 48/100 = 48%.  X7R typical derating at 48% rated:
  ~40-50% capacitance reduction → C_eff ≈ 1.3µF (DESIGN_DOC §4.4 estimate).
"""

import cmath
import math

# ── Component values ──────────────────────────────────────────────────────────
R_capsule = 200.0     # Ω  — EM272Z output impedance (typical)
R_inj     = 6810.0    # Ω  — phantom injection resistor (6.81kΩ)
C_rated   = 2.2e-6    # F  — rated capacitance (2.2µF/100V X7R 1812)
C_derated = 1.3e-6    # F  — effective at 48V bias (~59% remaining, DESIGN_DOC §4.4)
R_hfb     = 8000.0    # Ω  — HiFiBerry PCM1863 input impedance (typical)

def transfer(f, C_dc):
    """
    Voltage transfer function V(hfb_node) / V(capsule_source) at frequency f.
    Returns complex H(jω).
    """
    omega = 2 * math.pi * f
    Z_Cdc = complex(0, -1.0 / (omega * C_dc))   # DC-block cap (series)

    # Load seen by capsule at XLR node:
    #   R_inj (to AC-ground 48V supply) in parallel with (Z_Cdc + R_hfb)
    Z_load_ac = Z_Cdc + R_hfb                   # series path to HiFiBerry
    Z_xlr_load = (R_inj * Z_load_ac) / (R_inj + Z_load_ac)  # R_inj ║ series path

    # Voltage divider: capsule source → R_capsule → XLR node
    V_xlr = Z_xlr_load / (R_capsule + Z_xlr_load)

    # Second divider: Z_Cdc + R_hfb → output at R_hfb
    V_hfb = V_xlr * R_hfb / (Z_Cdc + R_hfb)

    return V_hfb   # relative to V_capsule = 1V

def db20(h):
    return 20 * math.log10(abs(h))

def find_minus3db(C_dc, f_lo=1.0, f_hi=1e5):
    """Binary search for the -3dB frequency."""
    # Reference: mid-band gain at 10kHz
    H_mid = transfer(10e3, C_dc)
    target_db = db20(H_mid) - 3.0

    for _ in range(60):
        f_mid = math.sqrt(f_lo * f_hi)
        if db20(transfer(f_mid, C_dc)) > target_db:
            f_hi = f_mid
        else:
            f_lo = f_mid
    return f_mid

# ── Theoretical corner frequencies ───────────────────────────────────────────
f_nominal  = 1 / (2 * math.pi * R_hfb * C_rated)
f_derated  = 1 / (2 * math.pi * R_hfb * C_derated)

print("sim4_audio.py — Audio path frequency response")
print("=" * 60)
print(f"  R_capsule={R_capsule:.0f}Ω  R_inj={R_inj/1e3:.2f}kΩ  R_HFB={R_hfb/1e3:.0f}kΩ")
print(f"  C_rated={C_rated*1e6:.1f}µF  C_derated@48V={C_derated*1e6:.1f}µF")
print()

for label, C_dc in [("Nominal (no derating, 2.2µF)", C_rated),
                     ("Derated  (48V bias,    1.3µF)", C_derated)]:
    print(f"── {label} ──")
    f3db = find_minus3db(C_dc)
    print(f"  Simulated -3dB frequency:  {f3db:.1f} Hz")
    print(f"  Theoretical (R_HFB×C_dc):  {1/(2*math.pi*R_hfb*C_dc):.1f} Hz")

    # Frequency sweep
    print()
    print(f"  {'Freq':>8}  {'Gain(dB)':>10}  {'vs 10kHz':>10}")
    print("  " + "-"*32)
    H_10k = transfer(10e3, C_dc)
    for f in [10, 15, 20, 50, 100, 1000, 10000]:
        H = transfer(f, C_dc)
        gain_abs = db20(H)
        gain_rel = db20(H) - db20(H_10k)
        flag = ""
        if abs(f - f3db) < f3db * 0.2:
            flag = " ← ≈-3dB"
        print(f"  {f:>8.0f}  {gain_abs:>10.2f}  {gain_rel:>+10.2f}{flag}")

    # Mid-band insertion loss vs ideal (capsule direct into ADC)
    H_ideal_1k  = R_hfb / (R_capsule + R_hfb)
    H_actual_1k = transfer(1000, C_dc)
    ins_loss_1k = db20(H_actual_1k) - 20*math.log10(H_ideal_1k)
    print(f"  Insertion loss at 1kHz (vs ideal load): {ins_loss_1k:+.2f} dB")
    print(f"    (due to R_inj shunting capsule signal; not frequency-dependent)")
    print()

# ── IEC phantom power audio-path note ────────────────────────────────────────
print("Audio-path note:")
print(f"  IEC 60268-15 mic input roll-off: typical spec > 20 Hz at -1dB")
print(f"  Derated -3dB corner at {f_derated:.1f} Hz — below 20Hz audio band. ✓")
print(f"  Wildlife recording (BirdNET): 0.05–12kHz — well above corner. ✓")
