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

#11 - Move C1 (VIN bypass 10µF) and C18 (BIAS bypass 100nF) closer to U1.
   Currently at y=59.72, 10.8–11.8mm from U1. Should be within 3–5mm of U1's VIN and BIAS pins (target y≈66–68, between C17 and U1). At current distance the bypass inductance makes these caps nearly useless against HF VIN noise.

#12 - Move FB1 to y≈71–72 to match the output filter cap row.
   FB1 is at y=79.27, output caps C3/C7/C10/C11 are at y=70.16 — a 9mm mismatch creating a 21.8mm diagonal +48V trace from FB1 to C11. Moving FB1 into the same y-band as the caps makes +48V a clean horizontal run and cuts FB1→SW1 trace length significantly.

#13 - Move C9 (bulk output cap) from y=80.89 to y≈77–78 (≤2mm from D1 cathode).
   Current D1→C9 gap is 6.25mm. The bulk cap must be immediately adjacent to D1 to absorb switching transients at their source; a 6mm stub adds inductance to the +48V_RAW node.

#14 - Rearrange FBX network (R1, R2, C12) to horizontal, move R1 closer to D1.
   Current vertical column at x≈147 puts R1 12.9mm from D1 (+48V_RAW source) and wedges the FBX traces between the timing row and FB1. A horizontal arrangement with R1 at x≈155–158 shortens the +48V_RAW sensing trace and reduces routing congestion.

#15 - Move J4 (R channel XLR pigtail) down to y≈86–87 to match J3 (L channel).
   J4 is at y=79.58, 10mm above R8/R9 (y=82–85), requiring a trace running upward from the bias resistors. J3 (L channel) is correctly below R6/R7. Moving J4 to the same y-band as J3 makes both channels consistent and straightens the XLR_R routing.
