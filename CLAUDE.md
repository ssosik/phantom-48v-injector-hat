# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project summary

KiCad 10 PCB design for a Raspberry Pi HAT that generates +48V phantom power from the Pi's 5V GPIO rail using an LT8362 boost converter, then injects it onto balanced audio lines feeding a HiFiBerry DAC2 ADC Pro. Full design rationale is in `DESIGN_DOC.md`.

## Commands

### Run DRC (headless)
```bash
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
  --output DRC.rpt \
  --format report \
  --all-track-errors \
  phantom-injector-hat.kicad_pcb
```

### Regenerate schematic wiring
```bash
python3 wire_schematic.py
```
Creates a `.bak` backup before writing. Run this whenever net labels or no-connect flags need to change.

### Re-place PCB components
```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 place_components.py
```
Requires KiCad's `pcbnew` Python module (bundled at `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/...`). Run **after** "Tools → Update PCB from Schematic" (F8) in the KiCad PCB editor.

## Architecture

### KiCad files
- `phantom-injector-hat.kicad_sch` — schematic (do not hand-edit wiring; use `wire_schematic.py`)
- `phantom-injector-hat.kicad_pcb` — PCB layout (S-expression format; can be scripted with Python or edited directly)
- `phantom-injector-hat.kicad_dru` — custom DRC rules (see constraints below)
- `phantom-injector-hat.kicad_pro` — project settings (board-level constraints like `min_resolved_spokes`)
- `fp-lib-table` — points to local custom LT8362 MSOP-16-EP footprint at `../ul_LT8362EMSE-PBF/KiCADv6/footprints.pretty`

### Python scripts

**`wire_schematic.py`** — single source of truth for net connectivity. The `NETLIST` dict maps `(ref, pin)` tuples to net names. Running the script strips all existing labels/no-connects and regenerates them from scratch. `LIB_PINS` provides pin endpoint coordinates in symbol space for each library component; `pin_abs()` applies the symbol rotation transform to get schematic-world coordinates.

**`place_components.py`** — single source of truth for component XY positions and rotations. The `PLACEMENTS` dict is the record of intent. It loads the board via `pcbnew.LoadBoard()`, sets each footprint's position and orientation, and saves. Update this dict to move parts, then run the script.

### Coordinate systems
- **KiCad schematic**: y-down, mm. Symbol libraries use y-up; `wire_schematic.py`'s `pin_abs()` handles the transform.
- **KiCad PCB**: y-down, mm. Origin near top-left. Board outline: x ≈ 100–165 mm, y ≈ 44–89 mm (65 × 45 mm).
- **B.Cu footprints** (like J1): local coords are mirrored. Transform: `PCB_x = center_x − y_local`, `PCB_y = center_y + x_local` for a footprint at -90°.

### Board layout zones (as built)
```
y≈47–56, x≈103–162: J1 GPIO socket (B.Cu, faces Pi below) + MH1/MH2 at the top corners
y≈57–78, x≈105–150: input filter (C6, C8, L2) on the left; boost converter (U1, L1, D1, Cx, Rx) centre/right
y≈79–88: injection row: R8/R9, J4, C15/C16, J2, C13/C14, J3, R6/R7, then R10/D2 and SW1
```

## Key design constraints

**J1 GPIO header**: `PinSocket_2x20_P2.54mm_Vertical` on **B.Cu**, at `(108.37, 53.91)` with rotation **-90°**. Socket housing faces down toward the Pi. Pads 2 and 4 (+5V_PI) are in the top row at the left end.

**LT8362 pin wiring**: Wire U1 by **pin name** (V_IN, SW, FBX, etc.), never by pin number. The NC spacer pins must be left unconnected (no-connect flag, not tied to GND). See `DESIGN_DOC.md` section 3.2.

**Custom DRC rules** (`.kicad_dru`):
- `signal`: 0.18mm clearance (tight — set to accommodate MSOP-16 U1 pads, which are 0.1956mm edge-to-edge), 0.2mm min track, 0.25mm min hole
- `power`: 0.5mm min track for +5V_PI, +5V_FILT, GND, SW_NODE, +48V_RAW, +48V (no extra clearance)
- `sw_node_isolation`: 0.5mm clearance between SW_NODE and all other nets
- `thermal_via`: 0.6mm min via diameter on GND (3×3 grid of 0.6/0.3mm vias under U1 EP; stitching vias are 0.8/0.4mm)

**KiCad 10 DRC rule syntax**: valid condition properties are `NetName` and `memberOf`. `Footprint`, `Reference`, and `Type` are not valid in rule conditions. Multiple constraints in one rule are fine; two rules with identical (or empty) conditions trigger a "same condition" error.

**Editing `.kicad_pcb` directly**: When flipping a footprint from F.Cu to B.Cu, all non-pad geometry (fp_line on F.CrtYd, F.SilkS, F.Fab) must have layer names changed to B.* **and** their local y-coordinates negated (so the physical PCB position is preserved). Pad y-coordinates must also be negated. Pad rotations shift by 180° (e.g., 90° → 270°). The `(justify mirror)` attribute must be added to all text `(effects ...)` blocks.

## DRC / ERC status (as of 2026-10-29)

DRC: fully routed, 0 unconnected pads, 1 accepted `track_width` error (0.25 mm +5V_FILT stub into U1, documented in `.kicad_dru`).
ERC: 0 errors, 13 warnings (vendor symbol pin types + library mismatch).

**Known open defect**: SW1 pins 1/2 are swapped in the schematic/PCB relative to `wire_schematic.py` (see README → Known issues).
