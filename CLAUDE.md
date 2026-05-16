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
python3 place_components.py
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
- **KiCad PCB**: y-down, mm. Origin near top-left. Board outline: x = 100–162 mm, y = 44–100 mm.
- **B.Cu footprints** (like J1): local coords are mirrored. Transform: `PCB_x = center_x − y_local`, `PCB_y = center_y + x_local` for a footprint at -90°.

### Board layout zones
```
x=100–113: J1 GPIO header (B.Cu, socket faces Pi below)
x=113–160, y=50–75: Boost converter (U1, L1, L2, D1, Cx, Rx)
x=113–160, y=75–98: Phantom injection (SW1/SW2, R6–R9, C13–C16, J3/J4)
x=119, y=90: J2 (2×3 to HiFiBerry J4)
```

## Key design constraints

**J1 GPIO header**: `PinSocket_2x20_P2.54mm_Vertical` on **B.Cu**, at `(108.37, 48.77)` with rotation **-90°**. Socket housing faces down toward the Pi. Pad 2 (+5V_PI) at PCB (108.37, 46.23); pad 4 (+5V_PI) at (110.91, 46.23).

**LT8362 pin wiring**: Wire U1 by **pin name** (V_IN, SW, FBX, etc.), never by pin number. The NC spacer pins must be left unconnected (no-connect flag, not tied to GND). See `DESIGN_DOC.md` section 3.2.

**Custom DRC rules** (`.kicad_dru`):
- `signal`: 0.18mm clearance (tight — set to accommodate MSOP-16 U1 pads, which are 0.1956mm edge-to-edge), 0.2mm min track, 0.25mm min hole
- `power`: 0.5mm min track, 0.3mm clearance for +5V_PI, +5V_FILT, GND, SW_NODE, +48V_RAW, +48V
- `sw_node_isolation`: 0.5mm clearance between SW_NODE and all other nets
- `thermal_via`: 0.6mm min via diameter on GND (for 3×3 stitching vias under U1 EP)

**KiCad 10 DRC rule syntax**: valid condition properties are `NetName` and `memberOf`. `Footprint`, `Reference`, and `Type` are not valid in rule conditions. Multiple constraints in one rule are fine; two rules with identical (or empty) conditions trigger a "same condition" error.

**Editing `.kicad_pcb` directly**: When flipping a footprint from F.Cu to B.Cu, all non-pad geometry (fp_line on F.CrtYd, F.SilkS, F.Fab) must have layer names changed to B.* **and** their local y-coordinates negated (so the physical PCB position is preserved). Pad y-coordinates must also be negated. Pad rotations shift by 180° (e.g., 90° → 270°). The `(justify mirror)` attribute must be added to all text `(effects ...)` blocks.

## DRC status (as of 2026-05-16)

25 warnings (silk overlaps and silk-over-copper — need GUI ref-text repositioning), 48 unconnected pads (routing not yet done), 0 errors. The 1 dangling track is a +5V_PI stub at (110.91, 51.31) on F.Cu.
