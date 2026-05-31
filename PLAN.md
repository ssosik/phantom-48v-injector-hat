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
