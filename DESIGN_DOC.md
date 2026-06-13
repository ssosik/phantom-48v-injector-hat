# Phantom Power Injector HAT

**Project**: P48 phantom-power injection HAT for Raspberry Pi 4B + HiFiBerry DAC2 ADC Pro + ESP P93 microphone preamplifier (phantom-mode variant).

**Revision**: 1.0 — initial design
**Date**: 2026-05-12
**Based on**: Analog Devices LT8362 datasheet, "Low I_Q, Low EMI, 400kHz, 48V Boost Converter with SSFM" typical application

---

## 1. System architecture

This HAT generates +48V phantom power from the Pi's 5V GPIO rail and injects it onto the audio lines heading to the HiFiBerry DAC2 ADC Pro's J4 balanced input header. The downstream P93 preamps derive their own +VE rail from the phantom feed via R10/R11/D1 on the preamp board.

```
Raspberry Pi 4B
  └─ +5V GPIO ──┐
                ▼
          [LT8362 boost converter, 400 kHz SSFM]
                │
                ▼ +48V rail
                │
          [Per-channel slide switch]
                │
                ▼
          [2× 6.81 kΩ 0.1% bias resistors per channel]
                │
                ▼
          XLR pins 2 and 3 ───────────► XLR pigtail ───► P93 preamp ───► EM272 mic
                │
                │ (audio AC, 48V DC)
                ▼
          [2.2 µF / 100V X7R DC-block caps]
                │
                ▼
          HiFiBerry DAC2 ADC Pro J4 header (audio only)
```

**Power budget**: 16 mA total @ 48V = 770 mW output. At 83% boost efficiency, draws ~185 mA from the Pi 5V rail. Within Pi 4B's GPIO 5V budget.

**Stack order**: Pi 4B (bottom) → HiFiBerry DAC2 ADC Pro (middle) → Phantom Injector HAT (top)

---

## 2. Bill of Materials

### 2.1 LT8362 boost converter section

**Package sizing strategy**: 0805 is the default for all signal and bypass passives — manageable with a fine-tip iron and tweezers, and TDK's high-voltage 0805 X7R line covers 50V/100V values that used to need 1210/1812. 1210 is reserved for the two bulk caps where capacitance density actually requires it (C6, C9). Schottky upsized from SOD-123 to SMA. The authoritative parts list is `BOM.csv`; this table mirrors it.

| Ref | Value | Description | Package | Mfr Part # | Qty/board |
|-----|-------|-------------|---------|------------|-----------|
| U1 | LT8362 | Boost controller, 60V SW, E-grade | MSOP-16-EP | LT8362EMSE#PBF | 1 |
| L1 | 22 µH | Shielded power inductor, Isat 2.55A | 5×5 mm SMT | Coilcraft XAL5050-223MEC | 1 |
| L2 | 2.2 µH | Input EMI filter inductor, Isat 8.4A | 7×7 mm SMT | Würth 74437324022 | 1 |
| D1 | B260A | 60V 2A Schottky, low VF | SMA / DO-214AC | Diodes Inc B260A-13-F | 1 |
| FB1 | 600Ω @ 100MHz, 2.3A | EMI filter ferrite bead | 0805 | Murata BLM21SP601SH1D | 1 |
| R1 | 1 MΩ 1% | FBX top divider | 0805 | Yageo RC0805FR-071ML | 1 |
| R2 | 34.8 kΩ 1% | FBX bottom divider (Vout = 47.6V) | 0805 | Yageo RC0805FR-0734K8L | 1 |
| R3 | 121 kΩ 1% | R_T, sets 404 kHz | 0805 | Yageo RC0805FR-07121KL | 1 |
| R4 | 22.1 kΩ 1% | V_C compensation | 0805 | Yageo RC0805FR-0722K1L | 1 |
| R5 | 100 kΩ 1% | EN/UVLO pull-up | 0805 | Yageo RC0805FR-07100KL | 1 |
| R11 | 100 kΩ 1% | SYNC/MODE → Burst+SSFM mode | 0805 | Yageo RC0805FR-07100KL | 1 |
| C1 | 10 µF / 16V X7R | V_IN bypass (on 5V rail) | 0805 | Murata GRM21BR71C106KE51L | 1 |
| C2 | 1 µF / 25V X7R | V_C compensation | 0805 | Murata GRM21BR71E105KA99L | 1 |
| C3 | 1 µF / 100V X7R | Output filter | 0805 | Murata GRM21BC72A105KA12L | 1 |
| C4 | 1 nF X7R | Compensation high-freq | 0805 | Yageo CC0805KRX7R9BB102 | 1 |
| C5 | 22 nF X7R | Soft-start | 0805 | Kemet (DigiKey 399-17886-1-ND) | 1 |
| C6 | 22 µF / 16V X7R | Bulk input | 1210 | Yageo CC1210KKX7R7BB226 | 1 |
| C7 | 0.1 µF / 100V X7R | Output bypass | 0805 | Yageo CS0805KKX7R0BB104 | 1 |
| C8 | 4.7 µF / 50V X7R | Input EMI filter | 0805 | TDK CGA4J1X7R1H475K125AC | 1 |
| C9 | 10 µF / 63V X7R | Bulk output | 1210 | Yageo CC1210KKX7R2BB106 | 1 |
| C10 | 0.1 µF / 100V X7R | Output bypass | 0805 | Yageo CS0805KKX7R0BB104 | 1 |
| C11 | 0.1 µF / 100V X7R | Output bypass | 0805 | Yageo CS0805KKX7R0BB104 | 1 |
| C12 | 4.7 pF C0G | FBX feedforward | 0805 | Murata GRM2195C1H4R7CA01D | 1 |
| C17 | 1 µF / 10V X7R | INTVCC bypass | 0805 | Murata GRM21BR71A105KA01L | 1 |
| C18 | 100 nF / 10V X7R | BIAS pin local bypass | 0805 | Murata GRM21BR71A104KA01L | 1 |

**Notes**:
- Reference designators C1–C9, R1–R5, L1–L2, D1, FB1, U1 mirror the LT8362 typical-application schematic to make cross-checking trivial. C10 and C11 replace the AD reference's C10a/C10b (split into two individually-placed 0805s), and C12 replaces the AD reference's C11 as the FBX feedforward cap. C17 (INTVCC bypass) and C18 (BIAS bypass) are added per LT8362 datasheet §7; R11 sets Burst+SSFM mode.
- C8 placement: on the **input** side of L2 (between Pi and the inductor), in parallel with C6 as part of the input EMI filter. C1 is the V_IN bypass on the **output** side of L2 (between the inductor and U1).
- C7, C3, C10, C11 are arranged in a vertical column around FB1 on the +48V output net (Pi-filter network).
- L1: BOM lists `Inductor_SMD:L_Coilcraft_XAL5030-XXX` as the KiCad footprint for the XAL5050 part. The XAL5030 and XAL5050 share the same 5×5 mm pad pattern; XAL5050 just has a taller body (5.1 mm vs. 3.1 mm). Verify clearance above L1 in the Pi/HAT/HiFiBerry stack.
- C9 voltage rating is 63V (not 50V) — 48V output plus switching transients make 50V marginal.

### 2.2 Phantom injection section

| Ref | Value | Description | Package | Mfr Part # | Qty/board |
|-----|-------|-------------|---------|------------|-----------|
| R6 | 6.81 kΩ 0.1% | XLR pin 2, L channel bias | 0805 | Panasonic ERA-6AEB6811V | 1 |
| R7 | 6.81 kΩ 0.1% | XLR pin 3, L channel bias | 0805 | Panasonic ERA-6AEB6811V | 1 |
| R8 | 6.81 kΩ 0.1% | XLR pin 2, R channel bias | 0805 | Panasonic ERA-6AEB6811V | 1 |
| R9 | 6.81 kΩ 0.1% | XLR pin 3, R channel bias | 0805 | Panasonic ERA-6AEB6811V | 1 |
| SW1 | SPDT slide | P48 enable, both channels (right-angle THT) | THT | C&K OS102011MA1QN1 | 1 |
| C13 | 2.2 µF / 100V X7R | DC-block, L+ to J4 | 0805 | TDK CGA4J1X7R2A225K125AC | 1 |
| C14 | 2.2 µF / 100V X7R | DC-block, L- to J4 | 0805 | TDK CGA4J1X7R2A225K125AC | 1 |
| C15 | 2.2 µF / 100V X7R | DC-block, R+ to J4 | 0805 | TDK CGA4J1X7R2A225K125AC | 1 |
| C16 | 2.2 µF / 100V X7R | DC-block, R- to J4 | 0805 | TDK CGA4J1X7R2A225K125AC | 1 |

**Note on R6–R9 matching**: phantom bias network CMRR depends on matching between the two resistors feeding each XLR pair. The 0.1% Panasonic ERA-6AEB6811V (or equivalent 0.1% E-series) gives roughly 60 dB CMRR contribution from the resistor pair. For wildlife recording this is excellent. If a single 0.1% spec is unavailable, hand-selecting four resistors from a 1% reel by sorting on a DMM works too.

**Note on C13–C16 sizing**: 100V X7R in 0805 is recent — TDK's CGA4J1X7R2A225K125AC delivers 2.2 µF / 100V in 0805 (3.2×1.6 mm with hand-solder pads). After DC bias derating at 48 V applied, the effective capacitance is ~1.3 µF, giving a ~15 Hz corner into PCM1863's 8 kΩ input. This was previously specified in 1812; the 0805 part has the same electrical performance with a smaller footprint, simpler hand assembly, and lower cost.

### 2.3 Connectors and indicators

| Ref | Value | Description | Mfr Part # | Qty/board |
|-----|-------|-------------|------------|-----------|
| J1 | 2×20 GPIO socket | RPi GPIO female stacking header | Sullins PPPC202LFBN-RC | 1 |
| J2 | 2×3 pin header 2.54mm | To HiFiBerry J4 | Generic | 1 |
| J3 | 1×3 pin header 2.54mm | XLR pigtail, L channel | Generic | 1 |
| J4 | 1×3 pin header 2.54mm | XLR pigtail, R channel | Generic | 1 |
| D2 | Green LED 3mm | +48V rail indicator (THT) | Generic 3mm green | 1 |
| R10 | 12 kΩ 1/4W | LED current limit (~3 mA @ 48V), 0805 | Yageo RC0805FR-0712KL | 1 |
| MH1, MH2 | M2.5 mounting hole | 2.7 mm drill; pairs with M2.5×11 mm standoff | — | 2 |

**Note on J1**: PPPC202LFBN-RC is a standard-pin-length female stacking header. Verify the pin projection is adequate to mate with the Pi GPIO when the HiFiBerry is sandwiched below. If clearance is tight, switch to a tall stacking header (e.g., SparkFun PRT-14017).

### 2.4 Per-build totals

| Item | 1 unit | 5 units (+10% spares) |
|------|--------|-----------------------|
| Total distinct line items | ~30 | ~30 |
| Total placements | ~42 | ~210 |
| Approx. line-item cost (excl. L1 direct, hardware, generic connectors, LED) | $23.30 | $116 |

See `BOM.csv` for the authoritative parts list with DigiKey part numbers, prices, and sourcing notes.

---

## 3. Net list and wiring

### 3.1 Nets

**Important — connect U1 by pin name, not pin number.** The pin numbers in earlier drafts of this document were inferred and have proven incorrect. The AD-provided LT8362 symbol shows the authoritative pin numbering; always wire by the pin name labels visible on the symbol (V_IN, SW, FBX, etc.).

| Net | Purpose | Connected to |
|-----|---------|--------------|
| `+5V_PI` | Pi GPIO 5V input | J1 pins 2, 4; L2 (input-side terminal); C6; C8 |
| `+5V_FILT` | Post-EMI-filtered 5V | L2 (output-side terminal); L1 (input-side terminal); U1 `V_IN`; C1 |
| `SW_NODE` | Boost switch node | L1 (output-side terminal); D1 anode; U1 `SW` |
| `+48V_RAW` | Boost output before output filter | D1 cathode; C9; FB1 (input-side terminal) |
| `+48V` | Filtered phantom rail | FB1 (output-side terminal); C3; C7; C10; C11; R10; SW1 (common terminal) |
| `+48V_SW` | Switched phantom rail (both channels) | SW1 (switched terminal); R6; R7; R8; R9 |
| `XLR_L_HOT` | L channel XLR pin 2 | R6 (XLR-side terminal); C13 (XLR-side terminal); J3 pin 2 |
| `XLR_L_COLD` | L channel XLR pin 3 | R7 (XLR-side terminal); C14 (XLR-side terminal); J3 pin 3 |
| `XLR_R_HOT` | R channel XLR pin 2 | R8 (XLR-side terminal); C15 (XLR-side terminal); J4 pin 2 |
| `XLR_R_COLD` | R channel XLR pin 3 | R9 (XLR-side terminal); C16 (XLR-side terminal); J4 pin 3 |
| `J4_L+` | HiFiBerry J4 L+ | C13 (J4-side terminal); J2 pin 5 |
| `J4_L-` | HiFiBerry J4 L- | C14 (J4-side terminal); J2 pin 6 |
| `J4_R+` | HiFiBerry J4 R+ | C15 (J4-side terminal); J2 pin 1 |
| `J4_R-` | HiFiBerry J4 R- | C16 (J4-side terminal); J2 pin 2 |
| `FBX` | Feedback to U1 | U1 `FBX`; R1 (between +48V_RAW and FBX); R2 (between FBX and GND); C12 (parallel with R1) |
| `VC` | Compensation | U1 `VC`; R4 (in series with C4 to GND); C2 (to GND) |
| `RT` | Frequency-setting | U1 `RT`; R3 (to GND) |
| `SS` | Soft-start | U1 `SS`; C5 (to GND) |
| `EN_UVLO` | Enable / undervoltage lockout | U1 `EN/UVLO`; R5 (to +5V_FILT, always-on enable) |
| `BIAS` | Internal bias | U1 `BIAS`; tied to +5V_FILT (verify in datasheet — see open item 4) |
| `INTVCC` | Internal regulator output | U1 `INTVCC`; bypass cap to GND (typ. 1 µF / 16V, verify in datasheet) |
| `SYNC_MODE` | Mode select | U1 `SYNC/MODE`; GND for SSFM-enabled operation (verify in datasheet) |
| `GND` | System ground | J1 pins 6, 9, 14, 20, 25, 30, 34, 39; J2 pins 3, 4; U1 `GND` and exposed pad; R2 (bottom terminal); R3 (ground-side terminal); C2, C4, C5, C7, C10, C11 (ground-side terminal each); C6, C8 (ground-side terminal each); C9 (ground-side terminal); C1 (ground-side terminal); D2 cathode; XLR pin 1 on J3 and J4 |

**Convention notes**:
- **All capacitors in this design are non-polarized ceramic** (X7R or C0G). Use `Device:C` (the symmetric symbol with two parallel plates), not `Device:C_Polarized`. Either terminal can connect to either net — orientation does not matter for assembly. Where the netlist describes a cap's terminals (e.g., "C13 (XLR-side terminal)"), it's identifying *which* net the terminal sits on, not implying a polarity requirement.
- **L1 (boost inductor)** sits between `+5V_FILT` (input side) and `SW_NODE` (output side). The "input-side terminal" is the one closer to U1's V_IN pin; the "output-side terminal" is the one closer to the SW pin and D1. Inductors are non-polarized; orientation doesn't matter.
- **L2 (input EMI filter)** sits between `+5V_PI` (input side, Pi GPIO) and `+5V_FILT` (output side, filtered). Non-polarized.
- **FB1 (output ferrite bead)** sits between `+48V_RAW` (boost converter output, ripple-bearing) and `+48V` (filtered rail, clean). Non-polarized.
- **D1 (Schottky)** is polarized. Anode → SW_NODE, cathode → +48V_RAW. Marked with a band on the cathode side.
- **D2 (LED)** is polarized. Anode (via R10) → +48V, cathode → GND. Marked with a flat on the cathode side, longer lead on the anode side.
- **R6–R9 (precision bias resistors)** are non-polarized. They sit between `+48V_L` or `+48V_R` and an XLR pin. "Other terminal" or "XLR-side terminal" in the netlist refers to the terminal connecting to the XLR pin (not the +48V side).

**Star ground note**: All "GND" pins are a single net in this design — there is no isolation barrier. The star point should be physically near U1's exposed pad (the IC's GND lead frame). J1's many GND pins all tie to this single GND net.

### 3.2 LT8362 pin connections (by name)

Pin numbers are deliberately omitted here. Connect using the pin function names as labeled on the AD-provided KiCad symbol. The MSOP-16-EP package has 16 mechanical pins but only 12 are electrically active (the other 4 are NC spacers); leave the NC pins unconnected.

| Pin name | Function | Connected to |
|----------|----------|--------------|
| `V_IN` | Power input | +5V_FILT, C1 |
| `EN/UVLO` | Enable / undervoltage lockout | R5 to +5V_FILT (always-on enable) |
| `SYNC/MODE` | Frequency sync / mode select | GND for internal-clock + SSFM-enabled operation (verify datasheet) |
| `SW` | Switch node | L1 (output-side terminal, the end opposite +5V_FILT), D1 anode |
| `GND` | Power ground | GND star point |
| `BIAS` | Internal bias supply | +5V_FILT (verify datasheet for minimum V_BIAS requirement) |
| `FBX` | Feedback | R1/R2 midpoint, C11 |
| `VC` | Compensation | R4-C4 series to GND, C2 to GND |
| `RT` | Frequency-setting | R3 (121 kΩ) to GND for ~400 kHz |
| `SS` | Soft-start cap | C5 (22 nF) to GND |
| `INTVCC` | Internal regulator output | Bypass cap to GND (typ. 1 µF / 16V) |
| `EP` (exposed pad) | Thermal + electrical ground | GND ground pour, with 3×3 thermal stitching vias to bottom-layer ground |
| `NC` × 4 | No connect | Leave open (do NOT tie to GND or any net) |

**Critical**: leaving NC pins unconnected is intentional. The LT8362 datasheet's Pin Functions section specifies these pins must be floating. Some KiCad symbol libraries draw NC pins as connectable to make ERC happy — if so, mark each NC pin with the "no connect" flag (`Q` in KiCad) rather than wiring it to any net.

### 3.3 J1 — Raspberry Pi GPIO (2×20)

Only 4 pins of the 40 are functionally connected. The rest pass through (because we're a stacked HAT and the HiFiBerry above us shares the same physical GPIO header).

| Pin | Signal | Connection |
|-----|--------|------------|
| 1 | +3.3V | Not used (pass-through only) |
| 2, 4 | +5V | +5V_PI net |
| 6, 9, 14, 20, 25, 30, 34, 39 | GND | GND net |
| All other pins | (Pi GPIO) | Not used, pass through |

### 3.4 J2 — HiFiBerry J4 ribbon (2×3)

Pinout matches the HiFiBerry DAC2 ADC Pro J4 header:

```
J2 layout (looking at top of HAT):
    1  2
    3  4
    5  6
```

| Pin | Signal | Net |
|-----|--------|-----|
| 1 | R- | J4_R- |
| 2 | R+ | J4_R+ |
| 3 | GND | GND |
| 4 | GND | GND |
| 5 | L+ | J4_L+ |
| 6 | L- | J4_L- |

### 3.5 J3, J4 — XLR pigtails (1×3)

Standard XLR pinout, easy to remember:

| Pin | Signal | Note |
|-----|--------|------|
| 1 | XLR pin 1 / GND | XLR shell, cable shield |
| 2 | XLR pin 2 / Hot | Audio + and phantom + |
| 3 | XLR pin 3 / Cold | Audio - and phantom + |

---

## 4. Critical design decisions and tradeoffs

### 4.1 Why this isn't a fully-isolated design (and what that costs)

The existing +9V PSU HAT uses a Murata NMH0515SC to provide **galvanic isolation** between Pi GND and the preamp's ISO_GND. This phantom injector HAT does not. The decision deserves more explanation than a one-liner because the noise tradeoff is real and worth understanding before deployment.

**What the +9V HAT's isolation was actually doing.** In that architecture, the P93's single-ended input stage is sensitive to any noise on its +9V supply rail — supply noise modulates the input transistor's bias and impresses itself directly onto the audio. Isolation prevents Pi-generated noise (digital switching, USB activity, GPIO toggling) from reaching that critical rail.

**What changes in phantom-power mode.** The P93's +VE rail is now regulated locally by D1 (its 10V Zener) from the phantom feed. By the time switching noise reaches the audio gain stage, it has passed through:

1. The output LC filter on the injector HAT (FB1 + capacitors)
2. The 6.81 kΩ phantom-injection bias resistors (an RC low-pass with the next cap stage)
3. The XLR cable (capacitance acts as additional filtering)
4. The P93's R10 and R11 (2.2 kΩ phantom-extraction resistors)
5. The P93's D1 Zener clamp (local re-regulation)
6. The P93's own bypass caps on the +VE rail

That's a six-stage filter between the switching node and the audio gain stage. Each stage attenuates 400 kHz substantially.

**The remaining noise risks (in approximate order of severity).**

1. **Switching radiation into audio traces** — the LT8362's SW node and inductor radiate, and they sit physically close to the audio path. This is the dominant risk and is addressed by PCB layout (section 5.3, switching loop layout) rather than by isolation. An isolated converter would radiate similarly; isolation doesn't help here.

2. **Common-mode injection through GND** — Pi switching activity creates noise on the shared GND net, which can propagate through the system. The balanced audio topology rejects most of it via the PCM1863's ~80 dB CMRR, but extreme cases (heavy USB traffic during recording) might leak through.

3. **Bus pumping** — Pi 5V rail variations (e.g., from Wi-Fi transmission bursts) propagate as brief +48V output variations, then through the six-stage filter to the audio.

Note that **none of these noise sources is what galvanic isolation primarily protects against**. Isolation protects against **ground loops** — situations where current flows through a "ground" reference because two ground points are at slightly different potentials. In this system, Pi GND, HiFiBerry GND, and XLR pin 1 all tie at one star point on the HAT, so there isn't a second ground point to form a loop with. Isolation would solve a problem that doesn't exist in this topology.

**How big the risk is in practice.** For wildlife recording with EM272 capsules:
- EM272 self-noise: ~14-20 dB SPL equivalent (fairly quiet, but not Sennheiser-MKH territory)
- Environmental noise: wind, traffic, other animals — typically 20-30 dB SPL even in quiet locations
- Long unbalanced cable runs: pick up RF and can add 5-10 dB of noise

Switching converter noise from a well-laid-out non-isolated injector HAT typically sits **below** the mic's self-noise floor. Quieter capsules (Sennheiser MKH-series, Schoeps CMC, etc.) might reveal the switching noise, but EM272 will not.

For comparison: commercial inline phantom supplies like the Rolls PB224 use non-isolated switching boost converters. Field recordists use them with high-end mics without complaint. The architecture is well-trodden.

**When to reconsider isolation.** If a future variant requires a quieter noise floor (e.g., recording very low-SPL ambient sounds, using ultra-quiet capsules, doing scientific bioacoustics measurements where any switching artifact would corrupt analysis), the architecture to revisit is:

```
Pi → existing +9V PSU HAT (isolated, +15V tapped) → new 15V→48V injector → HiFiBerry → P93
```

This brings isolation back via the existing well-debugged PSU HAT. Cost: an extra HAT in the stack (4 boards tall total), additional 5V→15V→48V efficiency loss, more layout/BOM work. For wildlife recording with EM272s, the cost outweighs the noise-floor benefit.

**Validation plan.** Build the non-isolated injector HAT, deploy it, and measure the noise floor with a known-quiet capsule pointed at a sound-absorbent surface. Compare against the same mic running on the existing +9V PSU HAT (battery-equivalent quiet baseline). If the noise floor difference is audible or measurable, reconsider the architecture. If it isn't, the simpler single-HAT design is validated for this use case.

### 4.2 Why 400 kHz, not 1 MHz

The Analog Devices reference design uses 400 kHz specifically for CISPR25 Class 5 EMI compliance — switching energy is below the AM radio band and the harmonics fall outside critical audio neighborhoods. Higher frequencies (1+ MHz) would give smaller passives but make EMI harder to control. 400 kHz × spread-spectrum is the manufacturer's recommended sweet spot for this output voltage.

### 4.3 Why 0.1% bias resistors

The 6.81 kΩ resistors feeding the two halves of each balanced line must match closely. A 1% mismatch in one resistor pair gives roughly 40 dB CMRR; 0.1% gives ~60 dB. Wildlife recordings are often made in environments with strong RFI (cell towers, weather radar), so CMRR margin matters.

### 4.4 Why 2.2 µF / 100V DC-block caps (not film)

The DC-block caps are 2.2 µF / 100V X7R ceramics — the compromise between size and audio quality. After DC bias derating (~50-60% at 48V applied), effective capacitance is ~1.3 µF, giving a 15 Hz corner into PCM1863's 8 kΩ input. Sub-audible and fine for wildlife. These are 0805 (TDK CGA4J high-V series); an "audiophile variant" board could swap to 4.7 µF / 63V WIMA MKS2 film caps with no other changes.

### 4.5 SSFM enabled

LT8362's spread-spectrum frequency modulation (SSFM) dithers the switching frequency over a small band, spreading switching energy across the spectrum rather than concentrating it in a tone. For audio applications this is particularly valuable — instead of a faint 400 kHz tone aliasing into the audio band, you get a faint broadband hiss that's much less perceptible. Enable via SYNC/MODE pin (verify exact configuration in datasheet).

---

## 5. PCB layout strategy

### 5.1 Board outline and stack

- Dimensions: Pi HAT standard, 65 mm × 56.5 mm
- Mounting holes: standard Pi HAT pattern (4× M2.5 at corners)
- Thickness: 1.6 mm
- 2-layer board (can fit on 2 layers; 4-layer would help SI but isn't required)

### 5.2 Critical layout zones

```
+-------------------------------------------+
|  XLR pigtails J3, J4    [top edge]        |
|  Slide switch SW1  ......... ~~~~~~~~~~~  |
|                                            |
|  Phantom injection: R6-R9, C12-C15        |
|  (analog, keep quiet)                     |
|                                            |
|  ============================== keep-out  |  ← break
|                                            |     between
|  Boost converter zone:                    |     analog and
|    U1, L1, D1, C6, C9, FB1, etc          |     switching
|  (switching, keep noisy contained)        |
|                                            |
|  J2 → HiFiBerry  [bottom-front edge]      |
|  J1 GPIO header  [bottom edge, centered]  |
+-------------------------------------------+
```

### 5.3 Switching loop layout (most critical)

The switching loop consists of U1's SW pin → L1 → D1 → C9 → back to U1's GND pin. This loop carries pulsed current at 400 kHz with fast edges (~10 ns). Keep this loop **physically as small as possible** — ideally under 5 mm² of enclosed area. Mistakes here radiate broadband noise.

Practical rules:
- Place C9 immediately adjacent to D1's cathode
- Place D1 immediately adjacent to L1's far pad
- Run the SW node (L1 to D1 anode) on top layer only, kept short
- Use a continuous ground pour on the bottom layer under the switching loop
- The bottom-layer ground pour acts as the return path; do not cut it with traces

### 5.4 Feedback trace (sensitive)

The FBX trace from R1/R2 midpoint to U1's `FBX` pin carries low-impedance high-frequency feedback. Keep it short (<10 mm), kept away from the SW node and L1. Run on bottom layer if the top is congested.

### 5.5 Ground strategy

Single GND net, but plan the layout such that:
- High-current switching ground (C6, C9, D1, U1 EP) shares a tight ground patch
- Audio ground (C12-C15, R6-R9, J2 GND, J3 GND, J4 GND) connects to that patch at one point only
- Pi GND comes in via J1 and ties at the same star point

### 5.6 LT8362 exposed pad layout

The MSOP-16-EP package has an exposed thermal pad on the underside of the chip that serves both as the IC's GND connection and as a heatsink. Layout requirements:

- **Pad size**: match the IC's EP dimensions per the LT8362 datasheet's "Package Information" page (verify against the official footprint, typically ~3.0×2.4 mm)
- **Thermal stitching**: 3×3 grid of 0.3 mm drill, 0.6 mm pad vias inside the EP footprint, plated through to a continuous ground pour on the bottom layer
  - This is essential for the iron-based assembly fallback (section 5.8.4)
  - Even with hot-plate reflow, these vias improve in-operation thermal dissipation and provide low-impedance ground return for the switching current
- **Soldermask**: open the soldermask over the EP pad in a slightly larger window than the pad itself, to ensure paste can spread cleanly during reflow
- **No silkscreen** over the EP area — it interferes with reflow

### 5.7 Stack clearances

- J1 header tops out at ~8.5 mm (Sullins PPPC202LFBN-RC plus mating socket)
- Slide switch: ~6 mm tall (within Z budget)
- SW node passives: <1 mm tall (SMD)
- WIMA film caps in future audiophile variant would be 5-7 mm — would need to check fit against HiFiBerry-above clearance, but the current 0805 ceramics are <1.5 mm.

### 5.8 Hand-assembly notes

All passives are 0805 or larger to support hand soldering with a fine-tip iron and tweezers. The LT8362's MSOP-16-EP package — with its exposed thermal pad — is the most challenging part of the assembly. Three methods are viable; the **recommended approach for this build is hot-plate reflow** (lowest skill floor, most reliable EP connection).

#### 5.8.1 Assembly method comparison

| Method | Setup cost | Time per board | Skill floor | LT8362 EP risk |
|---|---|---|---|---|
| Iron + via thermal stitching | $0 (existing iron) | ~20 min | High | Medium |
| Hot-air rework + solder paste | $30-50 | ~10 min | Medium | Low |
| **Hot-plate reflow + solder paste** | **$80** | **~5 min** | **Low** | **Very low** |
| PCB-assembly service (PCBWay etc.) | $40-80 setup + per-board fee | 0 (mailed back assembled) | None | None |

**Recommendation for this 5-unit build**: hot-plate reflow. The skill floor is much lower than iron methods, the equipment cost is modest and reusable for future projects, and the uniform heating eliminates the LT8362 exposed-pad gamble that iron-based methods involve.

#### 5.8.2 Hot-plate reflow workflow (recommended)

**Equipment**:
- Dedicated SMD reflow hot plate, ~100×100mm surface, with built-in lead-free profile
  - MINIWARE MHP30 (~$80) — well-regarded, USB-C powered, OLED display
  - AiXun T3A, Quicko T12-X (~$60-80) — similar capability
- Lead-free no-clean solder paste in syringe (Chip Quik SMD291AX10, ~$15 for 10cc)
- Fine-tip tweezers (curved or angled, ESD-safe)
- 10× magnifier or USB inspection scope for placement verification
- Optional but recommended: stainless-steel solder paste stencil from PCBWay (~$15, much faster than syringe application across 5 boards)

**Workflow**:

1. **Pre-warm the solder paste** — remove the syringe from the fridge 4+ hours before use. Bring to room temperature with the cap still on (prevents condensation on the paste).

2. **Apply paste to the PCB**:
   - **With syringe**: dispense a small even bead onto each SMD pad. Slightly excessive is OK; surface tension during reflow pulls it into shape. Critical: don't skimp on the LT8362's exposed-pad area — apply a solid uniform patch covering ~70% of the EP footprint.
   - **With stencil**: align stencil to PCB fiducials, squeegee paste across with a card or small spatula at ~45°, lift cleanly. Inspect under magnification.

3. **Place all SMD components** with tweezers:
   - The LT8362 first — light pressure, visual alignment, the orientation pin-1 dot must face the correct direction (verify against silkscreen)
   - Then larger parts (L1, L2 inductors, D1 SMA diode)
   - Then 1210 bulk caps (C6, C9)
   - Finally 0805 passives (everything else, including the 100V DC-block and output caps) — order doesn't matter as long as all are placed before reflow
   - Don't worry about minor misalignment for 0805+ parts — solder surface tension self-centers them during reflow

4. **Slide the loaded PCB onto the hot plate**:
   - Center the board so heat distribution is even
   - For a Pi HAT (65×56.5mm), the board fits comfortably on any 100mm+ surface

5. **Run the reflow profile** (most plates have a single button for this):
   - **Pre-heat**: ramp to 130-150°C over ~60 seconds (lets flux activate, prevents thermal shock cracking in ceramic caps)
   - **Soak**: hold at 150°C for ~60 seconds (heat spreads evenly through the board)
   - **Reflow**: push to 220-240°C for 20-30 seconds (solder melts, parts settle into their pads — you'll see the paste change from dull grey to shiny liquid)
   - **Cool**: turn off the plate but leave the board on it; let it cool to <50°C over a few minutes (slow cool reduces stress on ceramic caps)

6. **Inspect under magnification**:
   - Solder joints should be shiny and concave between pad and pin
   - No bridges between adjacent pins of the LT8362 (most likely failure mode)
   - All parts should be visibly aligned to their pads
   - Touch up any defects with an iron and flux paste

7. **Install through-hole parts** after the board has fully cooled:
   - J2, J3, J4 (small headers) first
   - SW1, SW2 (slide switches)
   - D2 (LED) + verify polarity against silkscreen
   - J1 (Pi GPIO 2×20 stacking header) **last** — it's tall and blocks access to everything else underneath

#### 5.8.3 Hot-air rework workflow (alternative)

If a hot plate isn't available, a hot-air rework station works:

1. Apply paste to LT8362 pads only (skip the rest for now)
2. Place LT8362 with tweezers
3. Reflow with hot air at 280-300°C, nozzle held ~20mm above the part for ~20 seconds — paste turns liquid
4. Let cool, verify with magnifier
5. Solder remaining SMD parts one at a time with iron + paste + small dabs of hot air for fine-pitch reflow
6. Install through-hole connectors last

This is slower (one-part-at-a-time) but works without the upfront hot-plate investment.

#### 5.8.4 Iron + thermal stitching workflow (fallback)

If neither hot plate nor hot air is available, the LT8362 EP can be soldered through bottom-side thermal vias:

1. PCB layout requires a 3×3 grid of 0.3mm vias inside the LT8362 EP footprint, plated through to a continuous ground pour on the bottom layer
2. Tin the bottom-side ground pour heavily around the via cluster
3. Place the LT8362 on the top, tack pins 1 and 9 (opposite corners) to hold it in place
4. From the bottom, heat the via cluster with a wide chisel tip at ~370°C — solder reflows up through the vias and bonds to the EP
5. Verify by gently rocking the part with tweezers — if it moves, the EP isn't bonded
6. Solder remaining 14 leaded pins by drag-soldering with flux paste, or pin-by-pin

This is the highest-skill method and the EP connection is the least reliable — risk a poorly-bonded EP causes thermal runaway during operation. Use only if other methods aren't possible.

#### 5.8.5 Solder paste handling notes

- **Storage**: refrigerator at 0-10°C (NOT freezer). Most pastes last 6 months refrigerated, only ~weeks at room temperature.
- **Pre-use**: 4+ hours at room temp before opening, cap still on. Cold paste applied to a warm board causes condensation that ruins joints.
- **After use**: cap the syringe, return to fridge. Mark the date on the syringe.
- **If paste appears dry or grainy**: it's expired. Order fresh.

#### 5.8.6 Tools list (consolidated)

**Essential** (regardless of method):
- Fine-tip tweezers, ESD-safe (curved or angled, ~$15)
- 10× magnifier or USB microscope ($30-100)
- Isopropyl alcohol + soft brush for flux cleanup
- Solder wick for fixing bridges
- Temperature-controlled iron, 0.4 mm fine conical tip, set to 350°C
- Liquid flux pen (rosin-based no-clean)

**For hot-plate workflow** (recommended):
- SMD reflow hot plate (~$80, e.g. MINIWARE MHP30)
- Lead-free no-clean solder paste in syringe (Chip Quik SMD291AX10)
- Optional: stainless-steel stencil from PCBWay (~$15, speeds paste application)

**For hot-air workflow**:
- Hot-air rework station ($30-50, look for adjustable temp and airflow)
- Same paste as above

#### 5.8.7 First-power testing protocol

After assembly, before plugging into the Pi:

1. **Visually inspect** the LT8362 and surrounding passives under magnification for bridges, missing parts, tombstoned caps
2. **Check continuity from +5V to GND** with a multimeter on the unpowered board — should read open or very high resistance (kΩ range or more). A low reading indicates a short and means stop, don't power up.
3. **Apply 5V via bench supply** with current limit set to 100 mA (well below expected ~185 mA draw) — board should current-limit immediately if there's a short, protecting the IC
4. **Measure +48V at the output filter** (after FB1) — should be 47-49V at no load
5. **Toggle each slide switch** and verify +48V appears on the corresponding XLR pins 2 and 3 (relative to pin 1)
6. **Increase current limit to 500 mA** and **plug in an actual P93 + EM272** — should see <100 mA total draw, +48V holding stable
7. **Inject audio at the EM272** (tap mic body, click, finger snap) — should see audio at the HiFiBerry J4 output via scope, or in the BirdNET-Pi recording stream

#### 5.8.8 Noise-floor validation (validates the non-isolated topology, see section 4.1)

After basic function is confirmed, before committing to the design across all 5 units:

1. **Set up a quiet test environment** — point the EM272 at a sound-absorbent surface (a cushion, foam, or inside a closed cabinet). Avoid metal surfaces (reflect HF). Reduce ambient noise to lowest practical level.
2. **Baseline recording (battery/PSU HAT mode)**: configure one P93 board for battery operation (per Rod's instructions: omit R10/R11/D1, reverse C5/C6, feed +9V from the existing PSU HAT). Record 30 seconds of silence into BirdNET-Pi or any DAW.
3. **Phantom-mode recording**: switch the same P93 back to phantom configuration, power it from the new injector HAT. Record 30 seconds of silence.
4. **Compare in audio editing software**:
   - Look at the RMS noise floor — should be within 1-3 dB between the two recordings
   - Listen for any tonal content around 400 kHz aliases (it shouldn't be present after the LT8362 spread-spectrum and the six-stage filter, but verify)
   - Look at the spectrum (FFT view) — should be a smooth broadband floor, no sharp tones
5. **If the phantom-mode recording shows audible or measurable tonal noise** (>5 dB worse than baseline):
   - Most likely cause: PCB layout — switching loop too large, ground pour discontinuous, audio traces near the SW node. Revise layout.
   - Less likely: insufficient output filtering. Try doubling C9 or adding a second ferrite stage.
   - Rarely: bus pumping from Pi 5V. Add bulk capacitance on the +5V_PI net.
6. **If layout fixes don't close the gap**, the architecture decision in section 4.1 should be revisited — pivot to Option D (use existing +9V PSU HAT's isolated +15V rail as input).



---

## 6. Open items to verify before fabrication

1. ~~**LT8362 pin numbering**~~ — resolved by using the AD-provided KiCad symbol. Wire by pin name, not pin number. See section 3.2.
2. ~~**V_FB (feedback reference voltage)**~~ — resolved (2026-06-12). LT8362 datasheet Electrical Characteristics (page 3): FBX Regulation Voltage in boost mode is **1.600 V typ** (1.568 V min / 1.636 V max), spec'd over full −40 to 125°C. With R1=1MΩ, R2=34.8kΩ: V_OUT = V_FBX × (1 + R1/R2) = 1.6 × 29.736 = **47.58 V typ**. Silicon-only spread 46.6–48.7 V; with ±1% resistor tolerance expands to ~46.0–49.3 V — well inside IEC 61938 (48V ± 4V) phantom-power spec. FBX pin current ≤10 nA produces 0.35 mV offset through R2; negligible vs 1.6 µA divider bias.
3. ~~**SYNC/MODE pin configuration for SSFM**~~ — resolved. Datasheet page 7 SYNC/MODE table: a 100kΩ resistor to GND selects Burst/SSFM mode. R11 = 100kΩ to GND is correct.
4. ~~**BIAS pin connection**~~ — resolved. Datasheet page 7: "INTVCC draws power from the BIAS pin if 4.4V ≤ BIAS ≤ VIN." With BIAS = +5V_FILT = VIN = 5V, both conditions are met (4.4V ≤ 5V ≤ 5V). This reduces VIN quiescent current from ~1200 µA to ~22 µA (55× improvement at light load). BIAS tied to +5V_FILT via C18 bypass is correct and optimal. "If unused, tie to GND" applies only when no suitable voltage is available.
5. ~~**HiFiBerry J4 pinout**~~ — resolved (2026-06-12). Re-verified §3.4 against HiFiBerry DAC2 ADC Pro datasheet (hifiberry.com/docs/data-sheets/datasheet-dac2-adc-pro/). **Bug found and fixed**: right channel +/− were swapped — §3.4 previously had pin 1 = R+ / pin 2 = R−, but the datasheet specifies pin 1 = in R− / pin 2 = in R+ (pin 1 is left bottom corner). Left channel and GND pins were correct. Without fix, the right channel would have inverted polarity vs the left, breaking stereo imaging and causing partial cancellation in any downstream mono sum. wire_schematic.py NETLIST and §3.4 table both updated; schematic regenerated.
6. ~~**C&K OS102011MA1QN1 footprint**~~ — resolved (2026-06-12). KiCad's `Button_Switch_THT:SW_Slide_SPDT_Angled_CK_OS102011MA1Q` footprint verified against C&K OS-series datasheet page 10. All critical dimensions match: 3 signal pins at 2.00 mm pitch (`.079"`), 2 mounting feet with 1.50 mm drill (`Ø.059"`) offset 2.10 mm (`.083"`) horizontally from the outer signal pins, total hole-pattern width 8.20 mm (`.323"`), body footprint 8.60 × 4.40 mm (`.339" × .173"`). Pin numbering matches SPDT schematic (pin 2 = common, pins 1/3 = throws). Single deviation: signal pin drill is 0.90 mm in KiCad vs 0.80 mm in datasheet — standard library practice (rounded to a common drill bit; 0.1 mm extra clearance eases insertion and stays within solderable annular-ring tolerance on the 1.5 mm pad).
7. ~~**Pi 5V current draw under transient (e.g., startup inrush of LT8362)**~~ — resolved (2026-06-12). Analytical analysis: t_ss = V_FBX × C5 / I_SS = 1.6V × C5 / 2µA. Output ramp current = C_OUT × (V_OUT/t_ss) where C_OUT ≈ 11.3 µF (C9 + C3 + C7/C10/C11). Input current = I_OUT × V_OUT / (V_IN × η) at η ≈ 85%. With original C5 = 10 nF → t_ss = 8 ms, I_IN ≈ **750 mA** for 8 ms (over the 600 mA HAT continuous spec). **Mitigation applied: C5 increased to 22 nF** → t_ss = 17.6 ms, I_IN ≈ **342 mA** (well under HAT spec). Schematic, BOM, and DigiKey order updated to match. Steady-state input current after startup is ~34 mA at full phantom load. Tradeoff: startup is 10 ms slower; irrelevant for phantom power. (Note: separate Pi 5V inrush event from C6+C8 charging at Pi power-on is governed by the Pi's own 5V slew rate and is independent of this analysis.)

---

## 7. KiCad workflow to finish this design

1. **Open KiCad 10**, create new project at `/Users/stevesosik/Documents/KiCad/phantom-injector-hat/`
2. **Add Analog Devices KiCad library** if not already installed (LT8362 symbol is in the official AD library — search "Symbol library" in KiCad's preferences)
3. **Place components** per section 2 BOM, using reference designators above
4. **Wire nets** per section 3 netlist
5. **Annotate** (or use the suggested annotations above directly)
6. **Run ERC** — should pass cleanly with only library mismatch warnings (cosmetic)
7. **Lay out PCB** per section 5
8. **Run DRC**
9. **Generate Gerbers** via manual export (KiCad 10 / PCBWay plugin compatibility issue still applies)

---

## 8. Future variants

- **v1.1**: WIMA MKS2 film caps for C12–C15 (audiophile variant, larger board area)
- **v2.0**: Add software-controlled P48 enable via Pi GPIO (replace SW1/SW2 with logic-level MOSFET high-side switches)
- **v2.1**: Add per-channel green LED to indicate phantom-active state
- **v3.0**: Integrate a small headphone amplifier for monitoring (would need a separate +9V/+12V rail from the existing PSU HAT — return to two-HAT stack)
