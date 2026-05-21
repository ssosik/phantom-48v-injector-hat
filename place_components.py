#!/usr/bin/env python3
"""
Component placement script for phantom-injector-hat.
Run AFTER "Tools > Update PCB from Schematic" (F8) in KiCad.

Board: 65×38mm Pi HAT (shortened to y=82 to clear HiFiBerry RCA jacks)
  TL corner: (100, 44)    TR: (165, 44)
  BL corner: (101, 82)    BR: (162, 82)   [1mm radius at BL, 3mm elsewhere]
  Mounting holes: (103.5,47.5), (161.5,47.5), (103.5,78.5), (161.5,78.5)
  J1 (40-pin GPIO): fixed at (108.37, 48.77) rot -90°

Layout zones:
  Boost stage:       x 113-160, y  50-75
  Phantom inject:    x 109-160, y  63-82
  SW1 near MH3:      x 109,     y  71

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
    # ── J1: GPIO header (fixed by Pi HAT spec) ──────────────────────────
    'J1':  (108.37, 48.77,  -90),

    # ── Mounting holes ──────────────────────────────────────────────────
    'MH1': (103.5,  47.5,    0),
    'MH2': (161.5,  47.5,    0),
    'MH3': (103.5,  78.5,    0),   # board bottom now y=82
    'MH4': (161.5,  78.5,    0),

    # ── Channel enable switch — left side near MH3 ───────────────────────
    # Single switch: gates +48V to +48V_SW feeding all four bias resistors.
    # At rot=90°, courtyard: x=[cx-2.7, cx+6.7], y=[cy-7.7, cy+3.7].
    # Note: courtyard overlaps C8/L2 (different heights — physically OK).
    'SW1': (109.5,  71.0,   90),   # phantom power enable (centered, was 65/77 for two switches)

    # ── Boost converter input ────────────────────────────────────────────
    'C6':  (113.5,  58.73,  180),  # 22µF/16V 1210 bulk input
    'C8':  (113.5,  62.79,  180),  # 4.7µF/50V 1210 EMI filter
    'L2':  (120.0,  61.0,     0),  # 2.2µH Würth HCI-7040

    # ── Control passives ─────────────────────────────────────────────────
    'C1':  (126.4,  58.6,   180),  # 10µF/50V 1210 VIN bypass
    'R5':  (130.3,  58.6,   180),  # 100kΩ EN/UVLO pullup
    'C17': (127.2,  62.41,  180),  # 1µF INTVCC bypass
    'C18': (127.2,  64.82,  180),  # 100nF BIAS bypass
    'C2':  (129.2,  68.4,   -90),  # 1µF VC comp
    'R4':  (131.8,  68.36,  -90),  # 22.1kΩ VC comp
    'C4':  (131.8,  72.8,   -90),  # 1nF VC HF comp

    # ── U1: LT8362 MSOP-16-EP ────────────────────────────────────────────
    'U1':  (133.5,  63.5,     0),

    # ── Feedback divider ─────────────────────────────────────────────────
    'R1':  (139.4,  72.06,   90),  # 1MΩ FBX top
    'C12': (142.7,  72.06,   90),  # 4.7pF FBX feedforward
    'R2':  (136.3,  72.06,  -90),  # 34.8kΩ FBX bottom

    # ── Timing / soft-start ──────────────────────────────────────────────
    'R3':  (140.0,  67.74,    0),  # 121kΩ RT
    'C5':  (140.0,  65.08,    0),  # 10nF SS
    'R11': (140.0,  62.41,    0),  # 100kΩ SYNC/MODE

    # ── L1: boost inductor ───────────────────────────────────────────────
    'L1':  (136.3,  57.2,     0),  # 22µH Coilcraft XAL5030

    # ── D1: Schottky rectifier ───────────────────────────────────────────
    'D1':  (143.7,  58.0,     0),  # SMA

    # ── Output bulk + filter chain ───────────────────────────────────────
    'C9':  (149.6,  56.44,   90),  # 10µF/50V 1210 bulk output
    'FB1': (151.2,  61.65,  180),  # 1206 ferrite bead
    'C3':  (151.7,  64.95,  180),  # 1µF/100V 1206
    'C7':  (151.7,  68.12,  180),  # 100nF 0805
    'C10': (151.7,  71.3,   180),  # 100nF 0805
    'C11': (151.7,  74.47,  180),  # 100nF 0805

    # ── LED indicator ────────────────────────────────────────────────────
    'R10': (154.6,  55.5,     0),  # 12kΩ LED current limit
    'D2':  (161.0,  55.42,    0),  # Green LED 3mm THT

    # ── XLR pigtail connectors — right side between boost caps and bottom
    # 1×3 vertical header at rot=90°. Using correct rot=90° formula:
    #   PCB_x = cx + local_y,  PCB_y = cy - local_x
    # Header courtyard (local x=[-1.5, 5.58], y=[-1.5, 1.5]):
    #   PCB x=[cx-1.5, cx+1.5],  PCB y=[cy-5.58, cy+1.5]
    # J4 at cy=73.5: y=[67.92, 75.0] — 1mm gap from MH4 courtyard top (y=76)
    'J3':  (156.25, 64.0,    90),  # L channel XLR
    'J4':  (156.25, 73.5,    90),  # R channel XLR (moved up from 74.5 to clear MH4)

    # ── Phantom injection bias resistors (0805) ──────────────────────────
    # Moved right to clear SW2 courtyard right edge at x≈116.2
    'R6':  (119.0,  75.5,     0),  # 6.81kΩ L+  (was x=116)
    'R7':  (119.0,  79.0,     0),  # 6.81kΩ L-  (was x=116)
    'R8':  (122.5,  75.5,     0),  # 6.81kΩ R+  (was x=120.5)
    'R9':  (122.5,  79.0,     0),  # 6.81kΩ R-  (was x=120.5)

    # ── DC-block caps 1812, rot=90° (4.06mm wide in X, 6.46mm tall in Y) ─
    # Four caps in two x-columns, two y-positions each.
    # Column 1 (x=127): C13 top, C15 bottom  — gap between them: 0.54mm
    # Column 2 (x=136): C14 top, C16 bottom  — clear of U1 (x≤136.8, y≤65.8)
    'C13': (127.0,  70.0,    90),  # 2.2µF L+
    'C14': (120.5,  70.0,    90),  # 2.2µF L- (moved left of C13 to clear R2 courtyard)
    'C15': (127.0,  77.0,    90),  # 2.2µF R+
    'C16': (136.0,  77.0,    90),  # 2.2µF R-

    # ── HiFiBerry ADC input — 2×3 placeholder (measure before finalizing)
    # J2 must align with HiFiBerry DAC2 ADC Pro J4 connector.
    # Measure HiFiBerry J4 offset from GPIO pin 1, then update this position.
    # Pin 1 is the footprint anchor; footprint extends +5.08mm in Y, +2.54mm in X.
    # At y=75.0: bottom pads at y≈80.1, courtyard bottom ≈y=81.1 — fits within y<82.
    'J2':  (143.0,  75.0,     0),  # 2×3 to HiFiBerry J4 (TBD)
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
        print(f"  {ref:5s}  ({x_mm:7.2f}, {y_mm:7.2f})  rot={rot:5}°")

    if missing:
        print(f"\nWARNING: not found on board (run Update PCB from Schematic first): {missing}")

    board.Save(PCB_PATH)
    print(f"\nSaved. Placed {len(placed)} footprints.")
    if missing:
        print(f"Re-run after F8 to place: {missing}")


if __name__ == '__main__':
    main()
