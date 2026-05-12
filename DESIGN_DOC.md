# Phantom Power Injector HAT

**Project**: P48 phantom-power injection HAT for Raspberry Pi 4B + HiFiBerry DAC2 ADC Pro + ESP P93 microphone preamplifier (phantom-mode variant).

**Revision**: 1.0 — initial design
**Date**: 2026-05-12
**Based on**: Analog Devices LT8362 datasheet, "Low I_Q, Low EMI, 400kHz, 48V Boost Converter with SSFM" typical application

---

## TODO

revisit choice of caps, considering use of large audio-friendly caps like WIMA MKS2 4.7µF / 63V

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

| Ref | Value | Description | Package | Mfr Part # | Qty/board |
|-----|-------|-------------|---------|------------|-----------|
| U1 | LT8362 | Boost converter, 60V SW | MSOP-16-EP | LT8362EMSE#PBF | 1 |
| L1 | 22 µH | Shielded power inductor, ≥500 mA Isat | 5×5 mm | Coilcraft XAL5030-223MEC | 1 |
| L2 | 2.2 µH | Input EMI filter inductor | 1812 | Würth 74437324022 | 1 |
| D1 | 60V Schottky | 2A, low VF | SOD-123 | Diodes Inc DFLS260-7 | 1 |
| FB1 | Ferrite bead | 600Ω @ 100MHz, 1A | 1206 | Würth 742792040 | 1 |
| R1 | 1 MΩ 1% | FBX top divider | 0603 | Yageo RC0603FR-071ML | 1 |
| R2 | 34.8 kΩ 1% | FBX bottom divider | 0603 | Yageo RC0603FR-0734K8L | 1 |
| R3 | 121 kΩ 1% | R_T, sets 400 kHz | 0603 | Yageo RC0603FR-07121KL | 1 |
| R4 | 22.1 kΩ 1% | V_C compensation | 0603 | Yageo RC0603FR-0722K1L | 1 |
| R5 | 100 kΩ 1% | EN/UVLO pull-up | 0603 | Yageo RC0603FR-07100KL | 1 |
| C1 | 10 µF / 50V X7R | V_IN bypass | 1206 | Murata GRM31CR71H106KA12L | 1 |
| C2 | 1 µF / 25V X7R | V_C compensation | 0603 | Murata GRM188R71E105KA12D | 1 |
| C3 | 1 µF / 100V X7R | Output filter | 0603 | Murata GRM188R72A105KE15D | 1 |
| C4 | 1 nF X7R | Compensation high-freq | 0603 | Standard X7R | 1 |
| C5 | 10 nF X7R | Soft-start | 0603 | Standard X7R | 1 |
| C6 | 22 µF / 16V X7R | Bulk input | 1210 | Murata GRM32ER71C226KE15L | 1 |
| C7 | 0.1 µF / 100V X7R | Output bypass | 0402 | Standard X7R | 1 |
| C8 | 4.7 µF / 50V X7R | Input EMI filter | 1206 | Murata GRM31CR71H475KA12L | 1 |
| C9 | 10 µF / 50V X7R | Bulk output | 1210 | Murata GRM32ER71H106KA12L | 1 |
| C10a | 0.1 µF / 100V X7R | Output bypass | 0402 | Standard X7R | 1 |
| C10b | 0.1 µF / 100V X7R | Output bypass | 0402 | Standard X7R | 1 |
| C11 | 4.7 pF C0G | FBX feedforward | 0402 | Standard NP0/C0G | 1 |

**Notes**:
- Reference designators C1–C11, R1–R5, L1–L2, D1, FB1, U1 mirror the LT8362 typical-application schematic exactly to make cross-checking trivial.
- C8 placement: between L2 input and the LT8362 V_IN. This is the input-side EMI filter.
- C7, C3, C10a, C10b are arranged around FB1 in a Pi-filter network on the output.

### 2.2 Phantom injection section

| Ref | Value | Description | Package | Mfr Part # | Qty/board |
|-----|-------|-------------|---------|------------|-----------|
| R6 | 6.81 kΩ 0.1% | XLR pin 2, L channel bias | 0805 | Susumu RR1220P-682-D | 1 |
| R7 | 6.81 kΩ 0.1% | XLR pin 3, L channel bias | 0805 | Susumu RR1220P-682-D | 1 |
| R8 | 6.81 kΩ 0.1% | XLR pin 2, R channel bias | 0805 | Susumu RR1220P-682-D | 1 |
| R9 | 6.81 kΩ 0.1% | XLR pin 3, R channel bias | 0805 | Susumu RR1220P-682-D | 1 |
| SW1 | SPST slide | P48 enable, L channel | RA PCB | C&K OS102011MA1QN1 | 1 |
| SW2 | SPST slide | P48 enable, R channel | RA PCB | C&K OS102011MA1QN1 | 1 |
| C12 | 2.2 µF / 100V X7R | DC-block, L+ to J4 | 1812 | Murata GRM43ER72A225KE01L | 1 |
| C13 | 2.2 µF / 100V X7R | DC-block, L- to J4 | 1812 | Murata GRM43ER72A225KE01L | 1 |
| C14 | 2.2 µF / 100V X7R | DC-block, R+ to J4 | 1812 | Murata GRM43ER72A225KE01L | 1 |
| C15 | 2.2 µF / 100V X7R | DC-block, R- to J4 | 1812 | Murata GRM43ER72A225KE01L | 1 |

**Note on R6–R9 matching**: phantom bias network CMRR depends on matching between the two resistors feeding each XLR pair. The 0.1% Susumu RR1220P series is matched within ±0.1%, giving roughly 60 dB CMRR contribution from the resistor pair. For wildlife recording this is excellent. If a single 0.1% spec is unavailable, hand-selecting four resistors from a 1% reel by sorting on a DMM works too.

### 2.3 Connectors and indicators

| Ref | Value | Description | Mfr Part # | Qty/board |
|-----|-------|-------------|------------|-----------|
| J1 | 2×20 stacking header | RPi GPIO | Samtec SSQ-120-03-T-D | 1 |
| J2 | 2×3 box header polarized | To HiFiBerry J4 | Würth 61300621121 | 1 |
| J3 | 1×3 pin header 2.54mm | XLR pigtail, L channel | Würth 61300311121 | 1 |
| J4 | 1×3 pin header 2.54mm | XLR pigtail, R channel | Würth 61300311121 | 1 |
| D2 | Green LED 3mm | +48V rail indicator | Kingbright WP710A10GD | 1 |
| R10 | 12 kΩ 1/4W | LED current limit (~3 mA @ 48V) | 0805 | Yageo standard | 1 |

### 2.4 Per-build totals

| Item | 1 unit | 5 units (+10% spares) |
|------|--------|-----------------------|
| Total distinct line items | 28 | 28 |
| Total placements | ~35 | ~175 |

---

## 3. Net list and wiring

### 3.1 Nets

| Net | Purpose | Connected to |
|-----|---------|--------------|
| `+5V_PI` | Pi GPIO 5V input | J1 pins 2, 4; L2 input; C6+; C8+ |
| `+5V_FILT` | Post-EMI-filtered 5V | L2 output; U1 V_IN (pin 1); C1+; C8 not connected here |
| `SW_NODE` | Boost switch node | U1 SW (pin 4); L1 right; D1 anode |
| `+48V_RAW` | Boost output before output filter | D1 cathode; C9+; FB1 left |
| `+48V` | Filtered phantom rail | FB1 right; C3+; C7+; C10a+; C10b+; D2 anode (via R10); SW1 input; SW2 input |
| `+48V_L` | L-channel phantom (after SW1) | SW1 output; R6; R7 |
| `+48V_R` | R-channel phantom (after SW2) | SW2 output; R8; R9 |
| `XLR_L_HOT` | L channel XLR pin 2 | R6; C12+ (anode); J3 pin 2 |
| `XLR_L_COLD` | L channel XLR pin 3 | R7; C13+ (anode); J3 pin 3 |
| `XLR_R_HOT` | R channel XLR pin 2 | R8; C14+ (anode); J4 pin 2 |
| `XLR_R_COLD` | R channel XLR pin 3 | R9; C15+ (anode); J4 pin 3 |
| `J4_L+` | HiFiBerry J4 L+ | C12- (cathode); J2 pin 5 |
| `J4_L-` | HiFiBerry J4 L- | C13- (cathode); J2 pin 6 |
| `J4_R+` | HiFiBerry J4 R+ | C14- (cathode); J2 pin 1 |
| `J4_R-` | HiFiBerry J4 R- | C15- (cathode); J2 pin 2 |
| `FBX` | Feedback to U1 | U1 FBX (pin 7); R1; R2; C11 |
| `VC` | Compensation | U1 V_C (pin 9); R4; C2 |
| `RT` | Frequency-setting | U1 R_T (pin 11); R3 |
| `SS` | Soft-start | U1 SS (pin 12); C5 |
| `EN_UVLO` | Enable | U1 EN/UVLO (pin 2); R5 (to +5V_FILT) |
| `BIAS` | Internal bias | U1 BIAS (pin 6); tie to +5V_FILT or leave floating (verify datasheet) |
| `INTVCC` | Internal regulator output | U1 INTVCC (pin 16); bypass cap (small, datasheet-specified) |
| `SYNC_MODE` | Mode select | U1 SYNC/MODE (pin 3); GND for SSFM-on operation (verify datasheet) |
| `GND_PI` | Pi ground | J1 pins 6, 9, 14, 20, 25, 30, 34, 39; J2 pins 3, 4; all decoupling cap returns; SW1/SW2 grounds (not used since SPST); C12-C15 are AC-only |

**Star ground note**: All "GND" nets are a single net in this design — there is no isolation barrier. The star point should be physically near U1's exposed pad (the IC's GND lead frame). J1's many GND pins all tie to this single GND net.

### 3.2 LT8362 pinout (MSOP-16-EP)

Reference: LT8362 datasheet, Pin Configuration section.

| Pin | Name | Function | Connected to |
|-----|------|----------|--------------|
| 1 | V_IN | Power input | +5V_FILT, C1 |
| 2 | EN/UVLO | Enable / undervoltage lockout | R5 to +5V_FILT (always-on) |
| 3 | SYNC/MODE | Frequency sync / mode | GND for SSFM enabled |
| 4 | SW | Switch node | L1, D1 anode |
| 5 | GND | Power ground | GND, also exposed pad |
| 6 | BIAS | Internal bias | +5V_FILT (see datasheet, BIAS recommended) |
| 7 | FBX | Feedback | R1, R2, C11 |
| 8 | (NC or repeat) | — | See datasheet |
| 9 | V_C | Compensation | R4, C2 |
| 10 | (NC or repeat) | — | See datasheet |
| 11 | R_T | Freq-setting resistor | R3 to GND |
| 12 | SS | Soft-start cap | C5 to GND |
| 13-15 | (per datasheet) | — | See datasheet pin diagram |
| 16 | INTV_CC | Internal regulator output | Bypass cap to GND |
| EP | Exposed pad | Thermal + ground | GND (must solder to ground pour) |

**IMPORTANT — verify in datasheet**: Pin assignments above are based on memory/inference. The LT8362 datasheet's "Pin Configuration" page in the front matter has the authoritative mapping. **Cross-check every pin number before completing the schematic in KiCad.**

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
| 1 | R+ | J4_R+ |
| 2 | R- | J4_R- |
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

### 4.1 Why this isn't a fully-isolated design

There is no galvanic isolation between the Pi 5V rail, the audio ground, and the XLR shield. All three are the same GND net. In commercial mixers, phantom supplies use isolated converters to keep switching noise from analog rails. In this system, there is only one ground anyway (Pi, HiFiBerry, and the XLR shell all tie together), so an isolation barrier would do nothing functional. Switching noise mitigation comes from input/output LC filtering and careful PCB layout, not isolation.

### 4.2 Why 400 kHz, not 1 MHz

The Analog Devices reference design uses 400 kHz specifically for CISPR25 Class 5 EMI compliance — switching energy is below the AM radio band and the harmonics fall outside critical audio neighborhoods. Higher frequencies (1+ MHz) would give smaller passives but make EMI harder to control. 400 kHz × spread-spectrum is the manufacturer's recommended sweet spot for this output voltage.

### 4.3 Why 0.1% bias resistors

The 6.81 kΩ resistors feeding the two halves of each balanced line must match closely. A 1% mismatch in one resistor pair gives roughly 40 dB CMRR; 0.1% gives ~60 dB. Wildlife recordings are often made in environments with strong RFI (cell towers, weather radar), so CMRR margin matters.

### 4.4 Why 2.2 µF / 100V DC-block caps (not film)

Earlier discussion settled on 2.2 µF / 100V X7R 1812 ceramics as the compromise between size and audio quality. After DC bias derating (~50-60% at 48V applied), effective capacitance is ~1.3 µF, giving a 15 Hz corner into PCM1863's 8 kΩ input. This is sub-audible and fine for wildlife. A future "audiophile variant" board could swap to 4.7 µF / 63V WIMA MKS2 film caps with no other changes.

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
|  Slide switches SW1, SW2 ... ~~~~~~~~~~~  |
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

The FBX trace from R1/R2 midpoint to U1 pin 7 carries low-impedance high-frequency feedback. Keep it short (<10 mm), kept away from the SW node and L1. Run on bottom layer if the top is congested.

### 5.5 Ground strategy

Single GND net, but plan the layout such that:
- High-current switching ground (C6, C9, D1, U1 EP) shares a tight ground patch
- Audio ground (C12-C15, R6-R9, J2 GND, J3 GND, J4 GND) connects to that patch at one point only
- Pi GND comes in via J1 and ties at the same star point

### 5.6 Stack clearances

- J1 header tops out at ~8.5 mm (Samtec SSQ-120-03-T-D plus mating socket)
- Slide switches: ~6 mm tall (within Z budget)
- SW node passives: <1 mm tall (SMD)
- WIMA film caps in future audiophile variant would be 5-7 mm — would need to check fit against HiFiBerry-above clearance, but the current 1812 ceramics are <2 mm.

---

## 6. Open items to verify before fabrication

1. **LT8362 pin numbering** — verify against datasheet Pin Configuration page, specifically: V_IN, SW, FBX, V_C, R_T, SS, EN/UVLO, BIAS, INTV_CC. Some sources show 16 pins, some show 10 pins (DFN variant). MSOP-16-EP has specific NC pins.
2. **V_FB (feedback reference voltage)** — the AD typical-application schematic uses R1=1M, R2=34.8k for 48V output, which implies V_FB ≈ 1.6V. Verify against the Electrical Characteristics table.
3. **SYNC/MODE pin configuration for SSFM** — datasheet should specify whether SSFM is enabled by tying SYNC/MODE to GND, to V_IN, or via a resistor.
4. **BIAS pin connection** — datasheet shows it tied to V_IN in some examples; verify our 5V V_IN is high enough to use BIAS or if it should be left floating.
5. **HiFiBerry J4 pinout** — confirmed pinout in section 3.4 above against the DAC2 ADC Pro datasheet PDF. Worth re-verifying before locking the board.
6. **C&K OS102011MA1QN1 footprint** — KiCad's `Switch:SW_SPST` symbol works for ERC but the PCB footprint needs to match the actual mechanical drawing. Pull from C&K's datasheet.
7. **Pi 5V current draw under transient (e.g., startup inrush of LT8362)** — should not exceed 600 mA on GPIO. C5 soft-start (10 nF) limits inrush; verify in LTspice if uncertain.

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
