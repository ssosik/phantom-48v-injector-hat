#!/usr/bin/env python3
"""
Component placement script for phantom-injector-hat.
Run AFTER "Tools > Update PCB from Schematic" (F8) in KiCad.

Board: 65×38mm Pi HAT (shortened to y=82 to clear HiFiBerry RCA jacks)
  TL corner: (100, 44)    TR: (165, 44)
  BL corner: (101, 82)    BR: (162, 82)   [1mm radius at BL, 3mm elsewhere]
  Mounting holes: (103.5,47.5), (161.5,47.5), (103.5,78.5), (161.5,78.5)
  J9 (40-pin GPIO, Pi HAT spec position): (108.37, 48.77) rot -90°
  J1 (40-pin GPIO, HiFiBerry top-side header): (108.37, 53.91) rot -90°
    — 2.6mm gap between J9 odd row and J1 even row

Layout zones:
  Boost stage:       x 113-162, y  50-82
  Phantom inject:    x 100-135, y  68-90
  SW1 near MH3:      x 107,     y  69

J2 (HiFiBerry connector) position is a placeholder — measure the HiFiBerry
DAC2 ADC Pro J4 connector position relative to pin 1 of the 2x20 GPIO header
before finalizing J2's placement.
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
    # ── J9: GPIO socket at Pi HAT spec position (B.Cu, faces Pi below) ──
    'J9':  (108.37,   48.77,   -90),

    # ── J1: GPIO socket connecting to HiFiBerry top-side header ──────────
    # HiFiBerry DAC2 ADC Pro top-side header is shifted from standard Pi
    # HAT position. Measured: 2.6mm gap (J9 odd row → J1 even row)
    # → center_y = 48.77 + 2.6 + 2.54 = 53.91mm
    'J1':  (108.37,   53.91,   -90),

    # ── Mounting holes ────────────────────────────────────────────────────
    'MH1': (103.5,    47.5,      0),
    'MH2': (161.5,    47.5,      0),
    'MH3': (103.5,    78.5,      0),
    'MH4': (161.5,    78.5,      0),

    # ── Channel enable switch ─────────────────────────────────────────────
    'SW1': (107.112,  69.1308,  -90),

    # ── Boost converter input ─────────────────────────────────────────────
    'C6':  (105.592,  59.4401,  -90),   # 22µF/16V 1210 bulk input
    'C8':  (108.4836, 59.4401,  -90),   # 4.7µF/50V 1210 EMI filter
    'L2':  (114.996,  61.1888,    0),   # 2.2µH Würth HCI-7040

    # ── Control passives ──────────────────────────────────────────────────
    'C1':  (158.7541, 59.7232,  180),   # 10µF/50V 1210 VIN bypass
    'R5':  (158.7408, 62.5172,    0),   # 100kΩ EN/UVLO pullup
    'C17': (152.7304, 65.4348,   90),   # 1µF INTVCC bypass
    'C18': (153.6956, 59.7232,  180),   # 100nF BIAS bypass
    'C2':  (150.0472, 65.4396,   90),   # 1µF VC comp
    'R4':  (147.4472, 65.4796,   90),   # 22.1kΩ VC comp
    'C4':  (147.4472, 61.0396,   90),   # 1nF VC HF comp

    # ── U1: LT8362 MSOP-16-EP ────────────────────────────────────────────
    'U1':  (153.8747, 70.5182,  -90),

    # ── Feedback divider ──────────────────────────────────────────────────
    'R1':  (142.6212, 71.7392,   90),   # 1MΩ FBX top
    'C12': (145.9212, 71.7392,   90),   # 4.7pF FBX feedforward
    'R2':  (149.022,  71.7392,  -90),   # 34.8kΩ FBX bottom

    # ── Timing / soft-start ───────────────────────────────────────────────
    'R3':  (150.4444, 76.7684,  -90),   # 121kΩ RT
    'C5':  (153.1044, 76.7684,  -90),   # 10nF SS
    'R11': (155.7744, 76.7684,  -90),   # 100kΩ SYNC/MODE

    # ── L1: boost inductor ────────────────────────────────────────────────
    'L1':  (159.7408, 67.8004,  -90),   # 22µH Coilcraft XAL5030

    # ── D1: Schottky rectifier ────────────────────────────────────────────
    'D1':  (159.7408, 74.6396,  -90),   # SMA

    # ── Output bulk + filter chain ────────────────────────────────────────
    'C9':  (161.3156, 80.0432,    0),   # 10µF/50V 1210 bulk output
    'FB1': (138.9636, 72.7204,    0),   # 1206 ferrite bead
    'C3':  (135.306,  71.6321,   90),   # 1µF/100V 1206
    'C7':  (132.136,  71.6321,   90),   # 100nF 0805
    'C10': (128.956,  71.6321,   90),   # 100nF 0805
    'C11': (125.786,  71.6321,   90),   # 100nF 0805

    # ── LED indicator ─────────────────────────────────────────────────────
    'R10': (137.8968, 80.3404,  -90),   # 12kΩ LED current limit
    'D2':  (137.8968, 84.5568,  -90),   # Green LED 3mm THT

    # ── XLR pigtail connectors ────────────────────────────────────────────
    'J3':  (126.9748, 87.0968,  180),   # L channel XLR
    'J4':  (106.35,   87.0968,  180),   # R channel XLR

    # ── Phantom injection bias resistors (0805) ───────────────────────────
    'R6':  (130.8008, 84.5568,  180),   # 6.81kΩ L+
    'R7':  (130.8008, 82.0168,  180),   # 6.81kΩ L-
    'R8':  (102.5052, 84.5568,    0),   # 6.81kΩ R+
    'R9':  (102.5052, 82.0168,    0),   # 6.81kΩ R-

    # ── DC-block caps 1812 ────────────────────────────────────────────────
    'C13': (123.0925, 84.5568,  180),   # 2.2µF L+
    'C14': (123.0925, 82.0168,  180),   # 2.2µF L-
    'C15': (110.2307, 84.5568,    0),   # 2.2µF R+
    'C16': (110.2307, 82.0168,    0),   # 2.2µF R-

    # ── HiFiBerry ADC input — 2×3 (B.Cu — body faces down toward HiFiBerry)
    # J4 pin 1 measured from MH1: +11.32mm east, +37.14mm south.
    # J4 pin 1 = R- (lower-right corner as viewed from below).
    # 4-tuple: (x, y, rot, layer) — script flips to B.Cu automatically.
    'J2':  (114.82,   84.64,    90, 'F.Cu'),  # 2×3 to HiFiBerry J4
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
