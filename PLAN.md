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

#13 - Move C9 (bulk output cap) closer to D1 cathode. Target ≤2mm.
   D1 and C9 are now both at x=158.47; gap is still 6.25mm (Δy only). The straight-column
   geometry is good but the gap needs to close. Move C9 up to y≈76–77 (≤2mm below D1).

#14 - FBX network: R2→U1 is 10.05mm, needs ≤8mm. R1→D1 is 12.44mm.
   Current positions: R1=(146.08,73.62), C12=(148.31,73.66), R2=(143.89,71.64).
   R2 is the high-impedance FBX sense node — the trace from R2 to U1 FBX pin is 10mm.
   R1→D1 at 12mm is less critical: R1 is 1MΩ and senses +48V_RAW, which is filtered DC
   after C9; noise coupling into FBX via R1 is attenuated ≈97% by the divider ratio.
   Primary fix: move R2 (and R1/C12 together) right/up until R2→U1 ≤8mm.
   With U1 at (153.87, 70.52), target R2 near (148–151, 71–73).

#15 - :check: J4 vs J3 inconsistency: incorrect, close this item.
   J4 is 2.54mm above R8, J3 is 2.54mm below R6 — both are exactly one pin pitch from their
   bias resistors, symmetric by design. No issue.
