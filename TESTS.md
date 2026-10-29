# Tests and Simulations

## Headless checks (run any time)

The Python checks need KiCad's bundled interpreter (it ships `pcbnew`):

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
```

### Net connectivity — drift checker
```bash
# After every "Update PCB from Schematic" (F8):
$KPY check_netlist.py

# Re-save golden when you intentionally change the schematic:
$KPY check_netlist.py --save

# Print the full current netlist:
$KPY check_netlist.py --dump
```
Compares the 24 named nets against `netlist_golden.json`.
Ignores `unconnected-` auto-names so unused J1 GPIO pins don't generate false positives.
Exits 0 on clean match, exits 1 and prints per-net diffs on any drift.

The golden file records what the PCB *is*, not what it *should be*: re-saving it
after a bad schematic change bakes the mistake in. Review the diff before `--save`.

### DRC — PCB design rules
```bash
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
  --output DRC.rpt \
  --format report \
  --all-track-errors \
  phantom-injector-hat.kicad_pcb
```
Run after every routing session. Current baseline (2026-10-29): 1 error (accepted
0.25 mm `+5V_FILT` stub into U1, documented in `.kicad_dru`), 0 unconnected pads.
Goal before fabrication: 0 unconnected, only documented exceptions.

### ERC — schematic electrical rules
```bash
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc \
  --output ERC.rpt \
  phantom-injector-hat.kicad_sch
```
Current baseline (2026-10-29): 0 errors, 13 warnings. One is a library-symbol mismatch on U1;
the other 12 are `pin_to_pin` warnings because the vendor LT8362 symbol declares its pins
as "Unspecified". Neither is a wiring fault.

---

## Simulations (`sims/`)

These use an idealized switch, not the vendor LT8362 model, so they check the passive
network around the IC rather than the IC's control loop.

| File | What it checks | Run with |
|------|----------------|----------|
| `sim1_boost_steady_state.cir`, `sim1_boost_check.cir` | DCM operation, inductor peak current, output ripple | `ngspice -b <file>` |
| `sim3_pi_filter.cir` / `.py` | Attenuation of the 404 kHz switching ripple at the Pi 5V rail | `ngspice -b` / `python3` (stdlib only) |
| `sim4_audio.cir` / `.py` | DC-block high-pass corner and in-band insertion loss | `ngspice -b` / `python3` (stdlib only) |

Results are recorded in PLAN.md #29–#33:
- **Boost**: IL_peak ≈ 0.39 A (L1 XAL5050-223), ripple ≈ 34 mV p-p, DCM at 16 mA load.
- **Pi rail filter**: −51.6 dB at 404 kHz (target ≤ −40 dB).
- **Audio path**: −3 dB at 8.8 Hz nominal, 15 Hz with X7R DC-bias derating (1.3 µF effective
  into the PCM1863's ~8 kΩ input).

### Not yet simulated
- **Load transient** with the real LT8362 model (LTspice; model from analog.com → LT8362 →
  Design Resources). Step 8 → 16 mA; output should stay within ±5% of 48 V.
  Compensation: C2 = 1 µF, R4 = 22.1 kΩ, C4 = 1 nF.

---

## Back-of-envelope checks

### Thermal
At η ≈ 85%, U1 dissipates roughly 0.15 × 5 V × 185 mA ≈ 140 mW (the IC, D1 and L1 share the
loss, so this overstates U1's share). With MSOP-16-EP θJB ≈ 40 °C/W and 9 thermal vias under the EP,
ΔT ≈ 6 °C above the PCB, which is well within limits.

### Trace voltage drop (+48V_SW bus)
0.5 mm wide, 1 oz (35 µm), ≈ 54 mm long:
R = 1.72e-8 × 0.054 / (0.0005 × 0.000035) ≈ 53 mΩ → 0.85 mV at 16 mA. Negligible.
