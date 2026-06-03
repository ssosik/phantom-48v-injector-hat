#1 - Decide if the HAT stack can be Pi -> Phantom Power Injector -> HiFiBerry ADC

   -> The HiFiBerry pin headers are not inline with the Pi pin headers, and the HiFiBerry has some tall components on the edge of the board opposite the pin headers.

#2 - Get proper placement of J2

#3 - Should there be separate GND planes? Or other separation of components?

#4 - how can I be sure this won't fry the HiFiBerry board, or the Pi?

#5 - what width traces should be used?

#6 - :check: Are two switches really necessary, or would one suffice? → Decision: one switch (SW1) controls both channels simultaneously. Phantom power is a board-level enable/disable. The EM272 capsules used here all require phantom, so per-channel independent switching adds no value. SW2 removed from design.

#7 - Locate our J2 connector on the bottom side of the board to match up with J2 of the HiFiBerry

#8 - should i add vias?

#9 - what component groups should be separated from the others, and by how much?

#10 - should the LED be on all the time, or only when the 48v switch is set?

## PCB layout optimizations (from placement review)

#11 - :check: Move C1 (VIN bypass 10µF) and C18 (BIAS bypass 100nF) closer to U1.
   Resolved: C1 and C18 moved to y=65.48, now 5.1–5.3mm from U1. Acceptable.

#12 - :check: D1→FB1 resolved. FB1 is now at (154.41, 80.22), 6.90mm from D1. ✓
   FB1 moved from x=128 to x=154, now sitting just left of D1/C9 column. Output side:
   FB1→C11 edge-to-edge = 0.82mm. Output cap row (C3–C11) now at y≈81 to the left of FB1.
   +48V_RAW runs D1 → FB1 (6.9mm) → filtered +48V left to cap row → injection resistors.

#13 - :check: D1→C9 resolved. Pad-to-pad on +48V_RAW = 2.68mm. ✓
   D1 cathode pad at (156.693, 73.076), C9 +48V_RAW pad at (156.693, 75.761) — same x,
   2.68mm apart. Prior 6.25mm figure was center-to-center; pad-to-pad is the correct
   metric. 2.68mm ≈ 2.7nH additional inductance — negligible at switching frequencies.

#14 - :check: FBX network resolved. R2→U1 = 3.71mm. ✓
   R2=(150.34, 68.07), U1=(153.87, 66.95) — 3.71mm separation. Excellent.
   R1→D1 = 12.64mm; accepted as non-critical (R1 is 1MΩ; noise into FBX attenuated
   ≈97% by divider ratio; +48V_RAW after C9 is filtered DC).

#16 - :check: L1/D1 x-offset resolved. Δx=1.27mm, SW_NODE pad-to-pad=3.43mm. ✓
   L1 SW_NODE pad at (157.963, 65.892), D1 SW_NODE pad at (156.693, 69.076).
   3.43mm on the hottest trace — excellent. 1.27mm lateral offset is negligible.

#15 - :check: J4 vs J3 inconsistency: incorrect, close this item.
   J4 is 2.54mm above R8, J3 is 2.54mm below R6 — both are exactly one pin pitch from their
   bias resistors, symmetric by design. No issue.

## Pre-routing checklist (from assembly/edge audit)

#17 - :check: SW1 pads are within board. Body overhang is by design.
   All SW1 pads at y=81.97mm (7mm inside board). Bbox extends to y=90.51mm because the
   switch housing/actuator extends 8.5mm below the pad row — panel-mount style. Copper OK.

#18 - :check: J9 not required. Board connects directly J1↔HiFiBerry; no Pi GPIO pass-through needed.

#19 - :check: C6/C8 pad gap confirmed safe. Actual pad width=1.175mm (not 2.8mm as assumed).
   Pad-to-pad gap = 2.89 − 2×0.725 = 1.44mm. Passes 0.18mm DRC rule by wide margin.

#20 - :check: C13/C14 and C15/C16 pad gap confirmed safe.
   Pad height (y-dimension) = 1.450mm → ±0.725mm. Gap = 2.54 − 2×0.725 = 1.09mm. Fine.

#21 - :check: 2×3 thermal via grid placed under U1 EP. ✓
   6 vias in 2 columns × 3 rows at 1.22mm pitch, centered at (146.89, 67.34) within 0.003mm.
   All /GND net, 0.8mm dia / 0.4mm drill — passes thermal_via DRC rule (min 0.6mm).
   3 additional GND stitching vias placed near boost section: (143.69, 65.30), (143.79, 70.89),
   (149.99, 69.88) — all GND net, same spec. Confirm these are intentional before pour.

#22 - :check: SW1 moved to x=154.6, directly below C3. +48V input is now a 5.08mm
   vertical trace (C3 pad at x=156.60 → SW1 pad2 at x=156.61). LED (D2/R10) moved
   to x≈138.6, forming a vertical column above the injection row.
   Routing plan (route before GND pour):
     • C3 → SW1 pad2: 5mm vertical at x≈156.6 (trivial)
     • SW1 pad1 (+48V_SW) west along y≈82 → R7 (x=132.5) → R8 (x=102.2)
     • Short stub from main bus → R10 pad1 at (138.56, 79.31): 2.7mm north of y=82
     • R6 and R9 are on y=84.66 — branch south from main bus
   D2 pad2 (GND) at y=87.233 — margin 1.61mm to board edge; same as J3, acceptable.

#23 - :check: R5 moved. Now at (143.51, 57.16), bbox right=147.85mm. Well clear of board edge.

## Fresh-eyes routing pre-flight (2026-06-03)

#24 - SW1 floating pads: pad3 and an unnamed pad have no net assignment.
   Verify these are the NC throw and mechanical retention pin — intentionally unconnected.
   Add no-connect markers in schematic to suppress ERC warnings.

#25 - J3 GND pin (pad1) is at y=87.198mm; board bottom edge at y=88.839mm → 1.641mm margin.
   Pad edge to board edge ≈ 0.84mm (1.6mm THT pad). Passes standard fab rules (JLCPCB 0.3mm,
   PCBWay 0.5mm). Flag if fab changes — this is the tightest pad on the board.

#26 - :check: +5V_PI fully routed — no vias needed. J1 is THT (PAD_ATTRIB_PTH); pads 2 and 4
   are directly accessible from F.Cu. Six 1.0mm-wide F.Cu tracks connect:
   J1:4 ↔ J1:2 (2.54mm) → diagonal/vertical → C6 → C8 → L2 (bus at y=59.716).
   Dangling track resolved — it is the track ending at J1 pad4.

#27 - :check: (superseded) +5V_FILT is also routed: 23mm bus from L2:2 at (117.55,59.72)
   east to junction at x≈142.5, branching north to R5 and south to C1 → U1 VIN.
   ⚠ ISSUE: Short stubs into U1 VIN pins (pad3, pad7) are 0.25mm wide — violates the
   `power` DRC rule (min 0.5mm). Redraw those stubs at ≥0.5mm before running DRC.
   Affected tracks: near (145.0,66.6), (145.5,67-68), (145.3,68.6).

#28 - assess the layout for hand-placed hot plate soldering. Are these components too close?
