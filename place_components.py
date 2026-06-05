#!/usr/bin/env python3
"""
Component placement script for phantom-injector-hat.
Run AFTER "Tools > Update PCB from Schematic" (F8) in KiCad.

Board: 65×44.84mm Pi HAT (shorter than standard 56.5mm to clear HiFiBerry RCA jacks)
  TL corner: (100, 44)      TR: (165, 44)
  BL corner: (100, 88.839)  BR: (165, 88.839)   [3mm radius at all corners]
  Mounting holes: (103.5,47.5), (161.5,47.5)
  J1 (40-pin GPIO, HiFiBerry top-side header): (108.37, 53.91) rot -90°

Layout zones:
  Input caps:        x 106-115, y  59-62
  Boost row:         x 144-165, y  60-68  (L1→D1→C9 horizontal)
  U1 + passives:     x 140-158, y  65-76
  Output cap column: x 156-160, y  66-78  (FB1 + C11→C3 vertical)
  Phantom inject:    x 100-145, y  79-88
  SW1 + LED:         x 138-165, y  79-88  (SW1 beside C3 column; D2/R10 at x≈138.6)

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
    # ── J1: GPIO socket connecting to HiFiBerry top-side header ──────────
    'J1':  (108.3700,  53.9100,  -90, 'B.Cu'),

    # ── Mounting holes ────────────────────────────────────────────────────
    'MH1': (103.5000,  47.5000,    0),
    'MH2': (161.5000,  47.5000,    0),

    # ── Channel enable switch ─────────────────────────────────────────────
    'SW1': (145.5736,  81.9660,    0),

    # ── Boost converter input ─────────────────────────────────────────────
    'C6':  (106.2484,  61.2781,  -90),   # 22µF/16V bulk input
    'C8':  (109.3472,  60.7531,  -90),   # 4.7µF/50V EMI filter
    'L2':  (114.9960,  59.7156,    0),   # 2.2µH Würth HCI-7040

    # ── Boost row: L1 → D1 → C9 horizontal at y≈61.5 ────────────────────
    'L1':  (135.1376,  61.3412,    0),   # 22µH Coilcraft XAL5050
    'D1':  (141.9768,  61.4936,    0),   # SMA Schottky
    'C9':  (149.0828,  61.4936,    0),   # 10µF/63V 1210 bulk output

    # ── U1: LT8362 MSOP-16-EP ────────────────────────────────────────────
    'U1':  (137.8554,  67.3393,    0),

    # ── Control passives (left of U1) ────────────────────────────────────
    'R5':  (134.4772,  56.9216,  180),   # 100kΩ EN/UVLO pullup
    'C1':  (132.4282,  65.8624,  180),   # 10µF/16V VIN bypass
    'C18': (132.4204,  68.3312,  180),   # 100nF BIAS bypass
    'C2':  (132.4125,  70.9218,  180),   # 1µF VC comp
    'C17': (135.7224,  72.0092,  -90),   # 1µF INTVCC bypass
    'R4':  (132.4524,  73.4824,  180),   # 22.1kΩ VC comp
    'C4':  (128.3885,  73.4824,  180),   # 1nF VC HF comp

    # ── Timing / soft-start (right of U1) ────────────────────────────────
    'R11': (143.3088,  65.3544,    0),   # 100kΩ SYNC/MODE
    'C5':  (143.3088,  68.2500,    0),   # 10nF SS
    'R3':  (143.3088,  71.1456,    0),   # 121kΩ RT

    # ── Feedback divider (below U1) ───────────────────────────────────────
    'R2':  (138.9748,  71.1252,  180),   # 34.8kΩ FBX bottom
    'C12': (140.9935,  73.6246,  180),   # 4.7pF FBX feedforward
    'R1':  (140.9560,  76.1240,  180),   # 1MΩ FBX top

    # ── FB1 + output cap column (vertical at x≈148.6) ────────────────────
    'FB1': (147.5588,  65.7100,   90),   # ferrite bead
    'C11': (148.6041,  69.2165,    0),   # 100nF 0805
    'C10': (148.6041,  71.7730,    0),   # 100nF 0805
    'C7':  (148.6041,  74.3295,    0),   # 100nF 0805
    'C3':  (148.6041,  76.8860,    0),   # 1µF/100V 0805

    # ── LED indicator ─────────────────────────────────────────────────────
    'R10': (138.1856,  80.3912,  -90),   # 12kΩ LED current limit
    'D2':  (138.2016,  83.8456,  -90),   # Green LED 3mm THT

    # ── XLR pigtail connectors ────────────────────────────────────────────
    'J3':  (127.6782,  86.7984,  180),   # L channel XLR
    'J4':  (107.0534,  79.1784,    0),   # R channel XLR

    # ── Phantom injection bias resistors (0805) ───────────────────────────
    'R6':  (131.5042,  84.2584,  180),   # 6.81kΩ L+
    'R7':  (131.5042,  81.7184,  180),   # 6.81kΩ L-
    'R8':  (103.2086,  81.7184,    0),   # 6.81kΩ R+
    'R9':  (103.2086,  84.2584,    0),   # 6.81kΩ R-

    # ── DC-block caps (0805) ──────────────────────────────────────────────
    'C13': (123.7959,  84.2584,  180),   # 2.2µF L+
    'C14': (123.7959,  81.7184,  180),   # 2.2µF L-
    'C15': (110.9341,  81.7184,    0),   # 2.2µF R+
    'C16': (110.9341,  84.2584,    0),   # 2.2µF R-

    # ── HiFiBerry ADC input — 2×3 ────────────────────────────────────────
    'J2':  (114.8200,  84.2400,   90, 'F.Cu'),  # 2×3 to HiFiBerry J4
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
