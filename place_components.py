#!/usr/bin/env python3
"""
Component placement script for phantom-injector-hat.
Run AFTER "Tools > Update PCB from Schematic" (F8) in KiCad.

Board: 65×44.84mm Pi HAT (shorter than standard 56.5mm to clear HiFiBerry RCA jacks)
  TL corner: (100, 44)      TR: (165, 44)
  BL corner: (100, 88.839)  BR: (165, 88.839)   [3mm radius at all corners]
  Mounting holes: (103.5,47.5), (161.5,47.5), (103.5,78.5), (161.5,78.5)
  J9 (40-pin GPIO, Pi HAT spec position): (108.37, 48.77) rot -90°
  J1 (40-pin GPIO, HiFiBerry top-side header): (108.37, 53.91) rot -90°
    — 2.6mm gap between J9 odd row and J1 even row

Layout zones:
  Boost stage:       x 113-162, y  50-82
  Phantom inject:    x 100-135, y  68-90
  SW1 near MH3:      x 107,     y  69

J2 (HiFiBerry connector): measured from MH1 +11.32mm east, +37.14mm south.
  Pin 1 (R−) is at the lower-right corner of J4 on the HiFiBerry.
"""

import sys
sys.path.insert(0, (
    '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework'
    '/Versions/3.9/lib/python3.9/site-packages'
))

import pcbnew

PCB_PATH = '/Users/stevesosik/Documents/KiCad/phantom-injector-hat/phantom-injector-hat.kicad_pcb'

# (x_mm, y_mm, rotation_degrees)  — or  (x_mm, y_mm, rotation_degrees, 'layer')
# Rotation follows KiCad convention: CCW positive, 0° = default footprint orientation.
# A 4-tuple layer name ('F.Cu' or 'B.Cu') triggers an automatic flip if needed.
PLACEMENTS = {
    # ── J9: GPIO socket at Pi HAT spec position (B.Cu, faces Pi below) ──
    'J9':  (108.37,    48.77,    -90),

    # ── J1: GPIO socket connecting to HiFiBerry top-side header ──────────
    # HiFiBerry DAC2 ADC Pro top-side header is shifted from standard Pi
    # HAT position. Measured: 2.6mm gap (J9 odd row → J1 even row)
    # → center_y = 48.77 + 2.6 + 2.54 = 53.91mm
    'J1':  (108.37,    53.91,    -90),

    # ── Mounting holes ────────────────────────────────────────────────────
    'MH1': (103.5,     47.5,       0),
    'MH2': (161.5,     47.5,       0),
    # ── Channel enable switch ─────────────────────────────────────────────
    'SW1': (107.112,   69.1308,  -90),

    # ── Boost converter input ─────────────────────────────────────────────
    'C6':  (105.592,   59.4401,  -90),   # 22µF/16V 1210 bulk input
    'C8':  (108.4836,  59.4401,  -90),   # 4.7µF/50V 1210 EMI filter
    'L2':  (114.9960,  59.7156,    0),   # 2.2µH Würth HCI-7040

    # ── Control passives ──────────────────────────────────────────────────
    'C1':  (158.7541,  59.7232,  180),   # 10µF/50V 1210 VIN bypass
    'R5':  (158.7408,  62.5172,    0),   # 100kΩ EN/UVLO pullup
    'C17': (152.7304,  65.4348,   90),   # 1µF INTVCC bypass
    'C18': (153.6956,  59.7232,  180),   # 100nF BIAS bypass
    'C2':  (150.0472,  65.4396,   90),   # 1µF VC comp
    'R4':  (147.4472,  65.4796,   90),   # 22.1kΩ VC comp
    'C4':  (147.4472,  61.0396,   90),   # 1nF VC HF comp

    # ── U1: LT8362 MSOP-16-EP ────────────────────────────────────────────
    'U1':  (153.8747,  70.5182,  -90),

    # ── Feedback divider ──────────────────────────────────────────────────
    'R1':  (142.6212,  71.7392,   90),   # 1MΩ FBX top
    'C12': (145.9212,  71.7392,   90),   # 4.7pF FBX feedforward
    'R2':  (149.022,   71.7392,  -90),   # 34.8kΩ FBX bottom

    # ── Timing / soft-start ───────────────────────────────────────────────
    'R3':  (150.4444,  75.9716,  -90),   # 121kΩ RT
    'C5':  (153.1044,  75.9716,  -90),   # 10nF SS
    'R11': (155.7744,  75.9716,  -90),   # 100kΩ SYNC/MODE

    # ── L1: boost inductor ────────────────────────────────────────────────
    'L1':  (159.7408,  67.8004,  -90),   # 22µH Coilcraft XAL5030

    # ── D1: Schottky rectifier ────────────────────────────────────────────
    'D1':  (159.7408,  74.6396,  -90),   # SMA

    # ── Output bulk + filter chain ────────────────────────────────────────
    'C9':  (159.7408,  80.8869,  -90),   # 10µF/50V 1210 bulk output
    'FB1': (140.2844,  71.6028,  -90),   # 1206 ferrite bead
    'C3':  (118.3184,  70.1589,  -90),   # 1µF/100V 1206
    'C7':  (121.4884,  70.1589,  -90),   # 100nF 0805
    'C10': (124.6684,  70.1589,  -90),   # 100nF 0805
    'C11': (127.8384,  70.1589,  -90),   # 100nF 0805

    # ── LED indicator ─────────────────────────────────────────────────────
    'R10': (133.5120,  79.6800,    0),   # 12kΩ LED current limit
    'D2':  (135.8648,  84.5568,  -90),   # Green LED 3mm THT

    # ── XLR pigtail connectors ────────────────────────────────────────────
    'J3':  (127.6782,  87.1984,  180),   # L channel XLR
    'J4':  (107.0534,  79.5784,    0),   # R channel XLR

    # ── Phantom injection bias resistors (0805) ───────────────────────────
    'R6':  (131.5042,  84.6584,  180),   # 6.81kΩ L+
    'R7':  (131.5042,  82.1184,  180),   # 6.81kΩ L-
    'R8':  (103.2086,  82.1184,    0),   # 6.81kΩ R+
    'R9':  (103.2086,  84.6584,    0),   # 6.81kΩ R-

    # ── DC-block caps 1812 ────────────────────────────────────────────────
    'C13': (123.7959,  84.6584,  180),   # 2.2µF L+
    'C14': (123.7959,  82.1184,  180),   # 2.2µF L-
    'C15': (110.9341,  82.1184,    0),   # 2.2µF R+
    'C16': (110.9341,  84.6584,    0),   # 2.2µF R-

    # ── HiFiBerry ADC input — 2×3 ────────────────────────────────────────
    # J4 pin 1 measured from MH1: +11.32mm east, +37.14mm south.
    # Pin 1 (R−) is at lower-right corner; connector extends left and up.
    # 4-tuple 'F.Cu' ensures the footprint stays on / flips back to F.Cu.
    'J2':  (114.82,    84.64,     90, 'F.Cu'),  # 2×3 to HiFiBerry J4
}


def main():
    print(f"Loading board: {PCB_PATH}")
    board = pcbnew.LoadBoard(PCB_PATH)

    # Build ref → footprint map
    fp_map = {fp.GetReference(): fp for fp in board.GetFootprints()}
    print(f"Found {len(fp_map)} footprints on board: {sorted(fp_map.keys())}")

    placed = []
    missing = []

    for ref, entry in PLACEMENTS.items():
        if len(entry) == 3:
            x_mm, y_mm, rot = entry
            target_layer = None
        else:
            x_mm, y_mm, rot, layer_name = entry
            target_layer = pcbnew.B_Cu if layer_name == 'B.Cu' else pcbnew.F_Cu

        if ref not in fp_map:
            missing.append(ref)
            continue

        fp = fp_map[ref]
        pos = pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))
        fp.SetPosition(pos)

        if target_layer is not None and fp.GetLayer() != target_layer:
            fp.Flip(pos, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)

        fp.SetOrientationDegrees(rot)
        placed.append(ref)
        layer_str = f"  layer={layer_name}" if target_layer is not None else ""
        print(f"  {ref:5s}  ({x_mm:8.4f}, {y_mm:8.4f})  rot={rot:6}°{layer_str}")

    if missing:
        print(f"\nWARNING: not found on board (run Update PCB from Schematic first): {missing}")

    board.Save(PCB_PATH)
    print(f"\nSaved. Placed {len(placed)} footprints.")
    if missing:
        print(f"Re-run after F8 to place: {missing}")


if __name__ == '__main__':
    main()
