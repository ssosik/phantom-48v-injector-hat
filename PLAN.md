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

#12 - :check: FB1 y-mismatch with output cap row resolved. New problem: D1→FB1 is 32mm.
   FB1 is now at (128.40, 69.11), only 1mm from C11 — alignment fixed. But the +48V_RAW
   trace from D1 (160.10, 74.64) to FB1 is now 32mm. Ripple from the switching node travels
   32mm unfiltered before reaching FB1. FB1 needs to move back right to ≤10mm from D1, while
   keeping FB1 at y≈69–70 to stay aligned with the output cap row.

#13 - Move C9 (bulk output cap) to y≈77–78 (≤2mm from D1 cathode).
   D1→C9 gap is still 6.25mm (both at x=160.10). The bulk cap must be immediately adjacent
   to D1 cathode to absorb switching transients; a 6mm stub adds inductance to +48V_RAW.

#14 - Find a stable position for the FBX network (R1, R2, C12) that satisfies both constraints.
   R1 must be close to D1 (the +48V_RAW source for feedback sensing) and R2 must be close to
   U1's FBX pin. Current position (R1 at 154.31,81.12 / R2 at 148.72,80.09) puts R1 8.69mm
   from D1 (improved) but R2 10.87mm from U1 (worse — was 7.2mm). The FBX trace now climbs
   10mm from y=80 to U1 at y=70.5, crossing the timing row at y=75.97. Target: position the
   network so R2→U1 ≤8mm and R1→D1 ≤10mm simultaneously.

#15 - :check: J4 vs J3 inconsistency: incorrect, close this item.
   J4 is 2.54mm above R8, J3 is 2.54mm below R6 — both are exactly one pin pitch from their
   bias resistors, symmetric by design. No issue.
