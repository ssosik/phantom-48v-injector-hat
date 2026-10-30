# TODO

## Before fabrication (any of these can change the board)

1. **Stack order (PLAN #37).** Settle this first: it decides how much layout the others need.
   Test-fit the Pi, the HiFiBerry and a 2×20 header on 11 mm standoffs.
   - Pi → this HAT → HiFiBerry: J1 must become a stacking header with pass-through pins
     (footprint change and a re-route along the top edge).
   - Pi → HiFiBerry → this HAT: confirm the HiFiBerry's top header has male pins for J1 to mate with.
   - Either way, check J1 pin length and L1's 5.1 mm height against the board above.
2. **J2 ↔ HiFiBerry J4 pin mapping (PLAN #38).** Decide ribbon vs. direct mate, then trace pin 1
   end to end (J2 pin 1 = R−). A 2×3 IDC ribbon swaps the odd and even rows. The fix may be
   flipping J2 or swapping labels in `wire_schematic.py`.
3. **Phantom switching transients (PLAN #36).** Check whether the HiFiBerry DAC2 ADC Pro clamps
   its analog inputs. If not, add a series R + BAV99 to the rails per leg (4×) after C13–C16, in
   the bottom row, and re-run `sims/sim4_audio` for in-band loss.

## Verification (no layout change expected)

4. **SW1 slide direction.** From the C&K datasheet or a meter on a real switch, find which slider
   position connects the common (pin 2) to pin 1. Then add ON/OFF end marks to the silkscreen.
5. **Load-transient sim in LTspice** with the real LT8362 model (TESTS.md "Not yet simulated"):
   step 8 → 16 mA, output within ±5 % of 48 V. Confirms C2/R4/C4 compensation before ordering.

## After 1–3 are resolved

- Re-run `./make_fab.sh`, check the Gerbers in a viewer, and tag the release that gets ordered.

## Ideas

- Revisit the choice of caps, e.g. large audio-friendly film caps like WIMA MKS2 4.7 µF / 63 V.
