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
