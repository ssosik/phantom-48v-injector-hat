#!/usr/bin/env python3
"""
sim3_pi_filter.py — Pi 5V rail switching noise attenuation
Analytical AC analysis of the input pi-filter.

Filter topology (noise injected at U1 VIN, propagates toward Pi rail):

  [Pi supply, 100mΩ src Z] ─── [C6=22uF ║ C8=4.7uF] ─── [L2=2.2uH/120mΩ] ─── [C1=10uF] ─── U1 VIN
                                      (Pi side)                (series)           (U1 side)

This is a π-topology:  C1 shunt  →  L2 series  →  C6║C8 shunt
Noise source: pulsed current demand from U1 VIN (AC 1A for normalised plot).
Output: voltage at Pi rail (= V(pi_rail) with 1A noise source).

At 404kHz, target: |Z_pi| < -40dBΩ  (< 10mV/A of switching noise)
"""

import cmath
import math

# ── Component values (from BOM) ──────────────────────────────────────────────
L2_H    = 2.2e-6     # Würth 74437324022 inductance
L2_DCR  = 0.120      # Ω  — estimated DCR for this part
C1_F    = 10e-6      # U1 VIN bypass, X7R 1210
C1_ESR  = 10e-3      # Ω
C6_F    = 22e-6      # Pi-side bulk cap, X7R 1210
C6_ESR  = 5e-3       # Ω
C8_F    = 4.7e-6     # Pi-side input filter cap, X7R 1210
C8_ESR  = 5e-3       # Ω
R_pi    = 0.100      # Ω  — Pi GPIO trace + connector source impedance

def z_cap(C_F, ESR, f):
    """Impedance of a capacitor with ESR."""
    omega = 2 * math.pi * f
    return complex(ESR, -1.0 / (omega * C_F))

def z_ind(L_H, DCR, f):
    """Impedance of an inductor with DCR."""
    omega = 2 * math.pi * f
    return complex(DCR, omega * L_H)

def analyse(f):
    """
    Transimpedance V(pi_rail) / I_noise  [Ω] for 1A noise current at U1 VIN.
    Returns (Z_pi_rail, Z_filt_node) as complex numbers.
    """
    # C1 shunt at U1 VIN side
    Z_C1 = z_cap(C1_F, C1_ESR, f)

    # L2 series element
    Z_L2 = z_ind(L2_H, L2_DCR, f)

    # C6 ║ C8 shunt at Pi side
    Z_C6 = z_cap(C6_F, C6_ESR, f)
    Z_C8 = z_cap(C8_F, C8_ESR, f)
    Z_C68 = (Z_C6 * Z_C8) / (Z_C6 + Z_C8)

    # Pi source impedance
    Z_pi_src = complex(R_pi, 0)

    # The circuit (current source I into filt_node, looking toward Pi supply):
    # I_noise → filt_node → C1 shunt to GND
    #                     → L2 → pi_rail → C6║C8 shunt to GND → R_pi → Vpi(AC=0)
    #
    # Node equations (1A current source at filt_node):
    # V_filt = I_noise * (Z_C1 ║ (Z_L2 + Z_pi_side))
    # where Z_pi_side = Z_C68 ║ Z_pi_src  [Pi source shunts C6║C8]
    # V_pi = V_filt * Z_pi_side / (Z_L2 + Z_pi_side)

    Z_pi_total = (Z_C68 * Z_pi_src) / (Z_C68 + Z_pi_src)  # C6║C8 in parallel with R_pi
    Z_l2_side  = Z_L2 + Z_pi_total                          # Looking from filt toward Pi
    Z_filt     = (Z_C1 * Z_l2_side) / (Z_C1 + Z_l2_side)   # filt node impedance (C1 ║ rest)

    # Voltages for 1A noise current into filt_node
    V_filt = 1.0 * Z_filt                                   # V_filt = 1A × Z_filt
    V_pi   = V_filt * Z_pi_total / Z_l2_side                # Divider across L2

    return V_filt, V_pi

def db20(z):
    """Magnitude in dBΩ (or dBV for 1A source)."""
    return 20 * math.log10(abs(z))

# ── Sweep and print key frequencies ──────────────────────────────────────────
freqs_of_interest = [10, 100, 1e3, 10e3, 100e3, 200e3, 404e3, 500e3, 1e6, 2e6]

print("sim3_pi_filter.py — Pi input filter attenuation")
print("=" * 60)
print(f"  L2={L2_H*1e6:.1f}µH/{L2_DCR*1000:.0f}mΩ  "
      f"C1={C1_F*1e6:.0f}µF  C6={C6_F*1e6:.0f}µF  C8={C8_F*1e6:.1f}µF")
print(f"  π-filter: [C1 shunt] → [L2] → [C6║C8 shunt]")
print()
print(f"  {'Freq':>10}  {'|V_filt|':>12}  {'|V_pi|':>12}  {'Attenuation':>14}")
print(f"  {'':>10}  {'(dBΩ)':>12}  {'(dBΩ)':>12}  {'(dB)':>14}")
print("  " + "-"*56)

for f in freqs_of_interest:
    V_filt, V_pi = analyse(f)
    db_filt = db20(V_filt)
    db_pi   = db20(V_pi)
    atten   = db_pi - db_filt
    label = ""
    if abs(f - 404e3) < 1e3:
        label = " ← fsw"
    print(f"  {f:>10.0f}  {db_filt:>12.1f}  {db_pi:>12.1f}  {atten:>12.1f} dB{label}")

print()
# Detail at switching frequency
f_sw = 404e3
V_filt, V_pi = analyse(f_sw)
atten_db = db20(V_pi) - db20(V_filt)
noise_per_amp = abs(V_pi) * 1000  # mV per amp of switching noise

print(f"At fsw = {f_sw/1e3:.0f} kHz:")
print(f"  Noise voltage at Pi rail:  {db20(V_pi):.1f} dBΩ  ({noise_per_amp:.3f} mV per amp of switch current)")
print(f"  Attenuation vs U1 VIN:     {atten_db:.1f} dB")
print(f"  Target:                    < -40 dB (< 10 mV/A)")
result = "PASS" if atten_db < -40 else "REVIEW"
print(f"  Result:                    {result}")
print()

# Estimate LC filter resonance frequency
# π-filter has two resonances; dominant one is L2 + C6║C8
C68 = C6_F + C8_F
f_res_lc = 1 / (2 * math.pi * math.sqrt(L2_H * C68))
print(f"π-filter L2+C68 resonance:   {f_res_lc/1e3:.1f} kHz")
f_res_c1 = 1 / (2 * math.pi * math.sqrt(L2_H * C1_F))
print(f"π-filter L2+C1  resonance:   {f_res_c1/1e3:.1f} kHz")
