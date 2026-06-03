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
    # HiFiBerry DAC2 ADC Pro top-side header shifted from standard Pi HAT.
    # Measured: 2.6mm gap (J9 odd row → J1 even row) → center_y = 53.91mm
    'J1':  (108.37,    53.91,    -90, 'B.Cu'),

    # ── Mounting holes ────────────────────────────────────────────────────
    'MH1': (103.5,     47.5,       0),
    'MH2': (161.5,     47.5,       0),

    # ── Channel enable switch — directly below C3, +48V input is 5mm vertical ──
    'SW1': (154.6060,  81.9660,    0),

    # ── Boost converter input ─────────────────────────────────────────────
    'C6':  (106.2484,  60.7531,  -90),   # 22µF/16V bulk input
    'C8':  (109.1400,  60.7531,  -90),   # 4.7µF/50V EMI filter
    'L2':  (114.9960,  59.7156,    0),   # 2.2µH Würth HCI-7040

    # ── Boost row: L1 → D1 → C9 horizontal at y≈61.5 ────────────────────
    'L1':  (144.1700,  61.4732,    0),   # 22µH Coilcraft XAL5030
    'D1':  (151.0092,  61.4936,    0),   # SMA Schottky
    'C9':  (158.1152,  61.4936,    0),   # 10µF/50V 1210 bulk output

    # ── U1: LT8362 MSOP-16-EP ────────────────────────────────────────────
    'U1':  (146.8878,  67.3393,    0),

    # ── Control passives (left column around U1) ──────────────────────────
    'R5':  (143.5096,  57.1552,  180),   # 100kΩ EN/UVLO pullup
    'C1':  (141.4606,  66.0960,  180),   # 10µF/50V 1210 VIN bypass
    'C18': (141.4528,  68.3312,  180),   # 100nF BIAS bypass
    'C17': (141.4020,  70.6680,  180),   # 1µF INTVCC bypass
    'C2':  (143.7481,  73.0464,  180),   # 1µF VC comp
    'R4':  (143.7880,  75.2908,  180),   # 22.1kΩ VC comp
    'C4':  (139.7241,  75.2908,  180),   # 1nF VC HF comp

    # ── Timing / soft-start (right column around U1) ──────────────────────
    'R11': (152.3412,  65.8420,    0),   # 100kΩ SYNC/MODE
    'C5':  (152.3412,  68.1788,    0),   # 10nF SS
    'R3':  (152.3412,  70.5156,    0),   # 121kΩ RT

    # ── Feedback divider (below U1 right) ─────────────────────────────────
    'R2':  (148.0072,  70.8712,  180),   # 34.8kΩ FBX bottom  (1.78mm pad→U1 FBX)
    'C12': (150.0259,  73.1064,  180),   # 4.7pF FBX feedforward
    'R1':  (149.9884,  75.3416,  180),   # 1MΩ FBX top

    # ── FB1 + output cap column (vertical at x≈157.6) ────────────────────
    'FB1': (156.5912,  66.8072,   90),   # 1206 ferrite bead
    'C11': (157.6365,  70.0584,    0),   # 100nF 0805
    'C10': (157.6365,  72.3444,    0),   # 100nF 0805
    'C7':  (157.6365,  74.6304,    0),   # 100nF 0805
    'C3':  (157.6365,  76.8860,    0),   # 1µF/100V 1206

    # ── LED indicator — vertical column at x≈138.6, above injection row ─────
    'R10': (138.5572,  80.3056,  -90),   # 12kΩ LED current limit
    'D2':  (138.5732,  84.6932,  -90),   # Green LED 3mm THT

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
