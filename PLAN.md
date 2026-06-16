#1 - :check: HAT stack confirmed: Pi → Phantom Injector HAT → HiFiBerry ADC.
   J1 (B.Cu socket) connects to Pi GPIO. J2 (F.Cu 2×3) connects to HiFiBerry J4.
   HiFiBerry header offset is handled by J2 position on this board. 2-hole mounting
   (MH1/MH2 at top edge) resolves height constraint from HiFiBerry's tall south-edge components.

#2 - :check: Get proper placement of J2

#3 - :check: Should there be separate GND planes? Or other separation of components?

#4 - :check: HiFiBerry and Pi safety verified by simulation.
   Pi rail: π-filter (C1→L2→C6‖C8) gives −51.6 dB attenuation at 404 kHz switching frequency
   — 11.6 dB margin over −40 dB target (PLAN #32). Noise at Pi rail: 0.107 mV/A switching current.
   +48V is galvanically isolated from the Pi 5V rail except through L2/C6/C8 filter.
   DC-block caps (C13–C16, 2.2µF/100V X7R) prevent phantom DC from reaching HiFiBerry inputs.
   Audio path corner: 15 Hz derated (PLAN #33) — well below 20 Hz audio band.

#5 - :check: what width traces should be used?

#6 - :check: Are two switches really necessary, or would one suffice? → Decision: one switch (SW1) controls both channels simultaneously. Phantom power is a board-level enable/disable. The EM272 capsules used here all require phantom, so per-channel independent switching adds no value. SW2 removed from design.

#7 - :check: Locate our J2 connector on the bottom side of the board to match up with J2 of the HiFiBerry

#8 - :check: 45 GND vias placed: 7 thermal vias under U1 EP (2×3 grid + 1 extra at corner)
   + 38 stitching vias across the board. All 0.8mm dia / 0.4mm drill, GND net.
   Passes thermal_via DRC rule (min 0.6mm). No signal vias needed (single-layer routing).

#9 - :check: Component separation reviewed and accepted.
   Boost section (U1, L1, L2, D1, Cx) is isolated from phantom injection area by SW1/C3 column.
   XLR connectors (J3/J4) and injection resistors (R6–R9) are in the southern zone x=100–135.
   GND pour provides isolation between zones. No additional separation required.

#10 - :check: should the LED be on all the time, or only when the 48v switch is set?

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

#34 - :check: 2-hole mounting configuration accepted (MH1 at 103.5,47.5 and MH2 at 161.5,47.5,
   both top edge). Board cannot extend south to Pi HAT standard 4-hole positions because the
   HiFiBerry board has tall components on its south edge that constrain the stack height.
   2-point mounting via top standoffs is the correct solution for this stack.

#24 - :check: SUPERSEDED (2026-06-15). SW1 pad 3 is no longer a no-connect.
   Switch was upgraded SPST → SPDT in the schematic; pad 3 is now wired to GND
   so flipping SW1 off actively drains the phantom rail (+48V_SW → GND through
   R6-R9) instead of letting it decay across the DC-block caps. Gives a cleaner
   audible mute. wire_schematic.py NETLIST line for SW1 now has all three pins
   bound: pin 1 = +48V, pin 2 = +48V_SW (common output to R6-R9), pin 3 = GND.
   See commit 7cfcf93.

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

## Simulation findings (2026-06-03)

#29 - :check: SYNC_MODE wiring confirmed correct.
   U1 pin 12 routes through R11 (100kΩ) to GND → Burst + SSFM mode enabled.
   SSFM spreads the 404 kHz tone across ±20%, replacing a discrete EMI tone with
   low-level broadband noise. Correct for audio applications. ✓

#30 - :check: V_FBX confirmed 1.600V (typ). DESIGN_DOC open item 2 closed.
   R1=1MΩ, R2=34.8kΩ → Vout = 1.60 × (1000/34.8 + 1) = 47.6V.
   Within IEC 61938 phantom power spec 48V ±4V (44–52V). ✓

#31 - :check: Boost converter checks passed (ngspice simulation).
   IL_peak = 0.390A  (limit: 1.4A Isat, XAL5050-223MEC)  — 3.6× margin ✓
   Output ripple = 33.7mV peak-peak  (limit: 100mV) ✓
   DCM confirmed at 16mA full load ✓
   Open-loop Vout = 46.1V at D=69.2%; closed-loop FB regulates to 47.6V ✓

#32 - :check: Pi 5V rail filter passes at 404 kHz (analytical simulation).
   Attenuation = −51.6 dB  (target: < −40 dB) — 11.6 dB margin ✓
   π-filter topology (C1 → L2 → C6║C8) gives 12 dB extra vs a simple LC.
   Noise at Pi rail: 0.107 mV per amp of switching current.

#33 - :check: Audio path −3dB corner confirmed (analytical simulation).
   Nominal (2.2µF, no bias derating): 8.8 Hz
   Derated  (1.3µF effective at 48V): 15.0 Hz  ← design operating point
   Both below 20 Hz audio band; BirdNET bandwidth (0.05–12 kHz) is flat. ✓
   Note: TESTS.md listed 10.6 Hz (used R_inj=6.81kΩ as reference impedance — wrong).
   Correct formula uses R_HFB=8kΩ (HiFiBerry PCM1863 input Z). Simulation confirms 15 Hz.
