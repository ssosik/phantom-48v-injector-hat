# Tests and Simulations

## Headless checks (run any time)

### DRC — PCB design rules
```bash
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc \
  --output DRC.rpt \
  --format report \
  --all-track-errors \
  phantom-injector-hat.kicad_pcb
```
Run after every routing session. Current baseline (2026-05-16): 25 silk warnings,
48 unconnected pads, 0 errors. Goal before fabrication: 0 errors, 0 unconnected.

### ERC — schematic electrical rules
```bash
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc \
  --output ERC.rpt \
  phantom-injector-hat.kicad_sch
```
Expected: no errors after SW1 NC pads are assigned no-connect markers (PLAN #24).
Unconnected J1 GPIO pins should already have no-connect flags.

---

## LTspice simulations

Download the LT8362 SPICE model from Analog Devices (free, requires ADI account):
https://www.analog.com/en/products/lt8362.html → "Design Resources" → SPICE model

### 1. Boost converter steady-state
Verify: 48V output at full load (~12mA), duty cycle (~90%), inductor peak current
within L1 saturation rating (Coilcraft XAL5030-223, Isat = 1.1A), output ripple < 100mV.

Key check: confirm LT8362 operates in discontinuous conduction mode (DCM) at 12mA load.
At DCM the FBX divider values (R1=1MΩ, R2=34.8kΩ) set Vout = 48V correctly.

### 2. Load transient response
Apply a step load from 6mA to 12mA (one capsule activating). Verify output stays within
±5% of 48V during transient. Compensation network: C2=1µF, R4=22.1kΩ, C4=1nF.

### 3. Pi 5V rail disturbance
Simulate what the LT8362 switching noise (~500kHz) looks like on the Pi's 5V rail after
the L2 + C6/C8 input filter (L2=2.2µH, C6=22µF/16V, C8=4.7µF/50V).
Target: ≥40dB attenuation at switching frequency.

### 4. Audio path frequency response
Model each channel: 6.81kΩ injection resistor in series with 2.2µF DC-block cap,
driving HiFiBerry ADC input impedance (~10kΩ typical).

Expected high-pass corner:
  f₋₃dB = 1 / (2π × 6810Ω × 2.2µF) ≈ 10.6 Hz

Confirm no interaction near 20Hz with realistic capsule source impedance.
Also confirm insertion loss at 1kHz and 10kHz is negligible (<0.1dB).

---

## Python checks

### Net connectivity verifier
A script can be written (~30 lines, using `pcbnew`) to read the PCB and assert that
each net connects exactly the expected set of component pads. Catches drift between
schematic and PCB that DRC misses (e.g., a pad assigned to the wrong net after
"Update PCB from Schematic"). Ask Claude Code to generate this if needed.

### Thermal estimate
At η≈85%, U1 dissipates P = (1−0.85) × Vin × Iin = 0.15 × 5V × ~96mA ≈ 72mW.
With MSOP-16-EP Rθjb ≈ 40°C/W (datasheet) and 6 thermal vias to GND plane:
  ΔTjunction ≈ 72mW × 40°C/W ≈ 2.9°C above PCB — well within limits.
No simulation required; this is a back-of-envelope pass.

### Trace voltage drop (#22 bus)
+48V_SW bus: 0.5mm wide, 1oz copper (35µm), length ≈ 54mm (C3 to R8).
  R_trace = ρ × L / (W × T) = 1.72e-8 × 0.054 / (0.0005 × 0.000035) ≈ 53mΩ
  V_drop at 12mA = 53mΩ × 12mA ≈ 0.64mV — negligible.
No simulation required.
