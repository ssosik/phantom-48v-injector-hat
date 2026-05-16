#!/usr/bin/env python3
"""
Component placement script for phantom-injector-hat.
Run AFTER "Tools > Update PCB from Schematic" (F8) in KiCad.

Board: 65×56.5mm Pi HAT
  TL corner: (100, 43.5)  TR: (165, 43.5)
  BL corner: (100, 100)   BR: (165, 100)
  Mounting holes: (103.5,47.5), (161.5,47.5), (103.5,96.5), (161.5,96.5)
  J1 (40-pin GPIO): fixed at (108.37, 48.77) rot -90°

Coordinate system: KiCad absolute mm (positive Y = down)

Layout zones (right of J1):
  Boost stage:       x 115-160, y  50-75
  Phantom inject:    x 115-160, y  75-95
"""

import sys
sys.path.insert(0, (
    '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework'
    '/Versions/3.9/lib/python3.9/site-packages'
))

import pcbnew

PCB_PATH = '/Users/stevesosik/Documents/KiCad/phantom-injector-hat/phantom-injector-hat.kicad_pcb'

# (x_mm, y_mm, rotation_degrees)
# Rotation follows KiCad convention: CCW positive, 0° = default footprint orientation
PLACEMENTS = {
    # ── J1: GPIO header (fixed by Pi HAT spec) ──────────────────────────
    'J1':   (108.37, 48.77,   90),

    # ── Boost converter input (left of L2 EMI filter) ───────────────────
    # C6, C8: input bulk/EMI caps, before L2
    'C6':   (117.0,  57.0,   90),   # 22µF/16V 1210, bulk input
    'C8':   (117.0,  63.0,   90),   # 4.7µF/50V 1210, EMI filter

    # L2: EMI filter inductor (~8.5mm courtyard)
    'L2':   (124.5,  60.0,    0),   # 2.2µH Würth HCI-7040

    # C1: VIN bypass, between L2 and U1
    'C1':   (130.0,  56.0,   90),   # 10µF/50V 1210

    # ── U1: LT8362 MSOP-16-EP ────────────────────────────────────────────
    # Left-side pins (1–8): EN/UVLO, VIN, INTVCC, BIAS, VC
    # Right-side pins (9–16): FBX, RT, SS, SYNC, SW2, SW1
    'U1':   (133.5,  63.5,    0),

    # ── Control passives — left/below U1 ─────────────────────────────────
    'R5':   (127.5,  57.5,    0),   # 100kΩ EN/UVLO pullup
    'C17':  (128.5,  61.5,   90),   # 1µF INTVCC bypass (place right at pin)
    'C18':  (128.5,  64.5,   90),   # 100nF BIAS bypass
    'C2':   (128.5,  68.0,   90),   # 1µF VC comp
    'R4':   (132.5,  70.5,    0),   # 22.1kΩ VC comp
    'C4':   (128.5,  71.5,   90),   # 1nF VC HF comp

    # Feedback divider — keep away from SW_NODE, routed to FBX pin
    'R1':   (130.0,  75.5,    0),   # 1MΩ FBX top (R1 top to +48V_RAW)
    'C12':  (134.5,  75.5,    0),   # 4.7pF FBX feedforward (parallel R1)
    'R2':   (130.0,  79.0,    0),   # 34.8kΩ FBX bottom (R2 bot to GND)

    # Timing / soft-start — right of U1 (these go to RT, SS, SYNC pins)
    'R3':   (140.0,  68.5,    0),   # 121kΩ RT
    'C5':   (140.0,  71.5,    0),   # 10nF SS
    'R11':  (140.0,  74.5,    0),   # 100kΩ SYNC/MODE to GND

    # ── L1: boost inductor, right of U1 SW pins (~6mm courtyard) ─────────
    'L1':   (142.5,  61.0,    0),   # 22µH Coilcraft XAL5030

    # ── D1: Schottky rectifier (anode ← L1, cathode → +48V_RAW) ─────────
    'D1':   (150.5,  58.0,    0),   # SMA, rot 0° puts cathode on right

    # ── Output bulk + filter chain (+48V_RAW → FB1 → +48V) ──────────────
    'C9':   (156.0,  62.0,   90),   # 10µF/50V 1210, bulk output
    'FB1':  (156.0,  67.5,   90),   # 1206 ferrite bead
    'C3':   (150.0,  67.0,    0),   # 1µF/100V 1206 output filter
    'C7':   (150.0,  70.5,    0),   # 100nF 0805 output bypass
    'C10':  (154.0,  70.5,    0),   # 100nF 0805 output bypass
    'C11':  (154.0,  73.5,    0),   # 100nF 0805 output bypass

    # ── LED indicator (top-right corner) ──────────────────────────────────
    'R10':  (152.5,  51.0,    0),   # 12kΩ LED current limit
    'D2':   (158.0,  51.0,    0),   # Green LED 3mm THT

    # ── Phantom injection — enable switches (right edge) ─────────────────
    # SW footprint (rot -90°): pads in column, actuator points in +X (off right edge)
    # Courtyard after -90° rot: X 157.3–166.7, Y 70.3–81.7 (SW1) / 81.7–93.3 (SW2)
    'SW1':  (160.0,  78.0,   90),   # L channel enable, actuator →right board edge
    'SW2':  (160.0,  90.0,   90),   # R channel enable, actuator →right board edge

    # Bias resistors (between switch output and DC-block caps)
    'R6':   (149.0,  79.5,   90),   # 6.81kΩ L+
    'R7':   (149.0,  83.0,   90),   # 6.81kΩ L-
    'R8':   (149.0,  87.0,   90),   # 6.81kΩ R+
    'R9':   (149.0,  90.5,   90),   # 6.81kΩ R-

    # DC-block caps 1812 (XLR signal nodes to HiFiBerry J4)
    'C13':  (140.0,  79.5,   90),   # 2.2µF L+
    'C14':  (140.0,  83.0,   90),   # 2.2µF L-
    'C15':  (140.0,  87.0,   90),   # 2.2µF R+
    'C16':  (140.0,  90.5,   90),   # 2.2µF R-

    # XLR pigtail headers (1×3, bottom area)
    'J3':   (131.5,  81.0,    0),   # L channel XLR (pin1=GND, 2=HOT, 3=COLD)
    'J4':   (131.5,  88.5,    0),   # R channel XLR

    # HiFiBerry J4 connector — POSITION TBD (measure physical board)
    # Placeholder: move after measuring HiFiBerry J4 relative to J1 pin-1
    'J2':   (119.0,  90.0,    0),   # 2×3 to HiFiBerry J4 (TBD)
}


def main():
    print(f"Loading board: {PCB_PATH}")
    board = pcbnew.LoadBoard(PCB_PATH)

    # Build ref → footprint map
    fp_map = {fp.GetReference(): fp for fp in board.GetFootprints()}
    print(f"Found {len(fp_map)} footprints on board: {sorted(fp_map.keys())}")

    placed = []
    missing = []

    for ref, (x_mm, y_mm, rot) in PLACEMENTS.items():
        if ref not in fp_map:
            missing.append(ref)
            continue

        fp = fp_map[ref]
        pos = pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))
        fp.SetPosition(pos)
        fp.SetOrientationDegrees(rot)
        placed.append(ref)
        print(f"  {ref:5s}  ({x_mm:6.1f}, {y_mm:6.1f})  rot={rot:4}°")

    if missing:
        print(f"\nWARNING: not found on board (run Update PCB from Schematic first): {missing}")

    board.Save(PCB_PATH)
    print(f"\nSaved. Placed {len(placed)} footprints.")
    if missing:
        print(f"Re-run after F8 to place: {missing}")


if __name__ == '__main__':
    main()
