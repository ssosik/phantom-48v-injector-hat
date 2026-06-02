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
   D1=(158.47, 71.08), C9=(158.47, 77.32) — same x column, Δy=6.25mm. The straight-column
   geometry is ideal for routing but the gap is too large. Move C9 up to y≈72–73 (≤2mm
   below D1). FB1 at y=76.66 and output cap row at y=77.70 will need to shift down
   slightly (~4mm) to restore the FB1→C11 clearance after C9 moves.

#14 - :check: FBX network resolved. R2→U1 = 3.71mm. ✓
   R2=(150.34, 68.07), U1=(153.87, 66.95) — 3.71mm separation. Excellent.
   R1→D1 = 12.64mm; accepted as non-critical (R1 is 1MΩ; noise into FBX attenuated
   ≈97% by divider ratio; +48V_RAW after C9 is filtered DC).

#16 - L1 x-offset from D1 is 3.1mm. Review after C9 repositioning.
   L1=(161.57, 64.24), D1=(158.47, 71.08) — Δx=3.10mm. The switching loop
   SW→L1→D1→C9 wants L1 and D1 co-linear in x to minimise loop inductance. A 3mm
   lateral offset adds a ~3mm jog on the SW node trace. Consider shifting L1 left
   to x≈158–159 to realign with D1.

#15 - :check: J4 vs J3 inconsistency: incorrect, close this item.
   J4 is 2.54mm above R8, J3 is 2.54mm below R6 — both are exactly one pin pitch from their
   bias resistors, symmetric by design. No issue.
