# Routing Guide — phantom-injector-hat

> Pre-routing guide, kept for the reasoning. The board is now fully routed; coordinates and zone
> suggestions below describe the plan, not necessarily the final layout.

## Trace Widths by Net

| Net | Current | Width | Notes |
|-----|---------|-------|-------|
| `SW_NODE` | peak ~2A, avg ~250mA | **1.5mm** | Most critical — keep stub SHORT |
| `+5V_PI` | ~300mA continuous | **1.0mm** | From J1 pins 2+4 |
| `+5V_FILT` | ~300mA continuous | **1.0mm** | After L2 filter inductor |
| `GND` | return for all | **copper pour** | Fill zone, don't route traces |
| `+48V_RAW` | ≤30mA | **0.5mm** | D1 cathode → C9 → FB1 |
| `+48V` | ≤30mA | **0.5mm** | FB1 output → C3/C7/C10/C11 → SW1 |
| `+48V_SW` | ≤30mA | **0.5mm** | SW1 out → R6/R7/R8/R9, R10 (LED) |
| `XLR_L_HOT`, `XLR_L_COLD` | audio + 7mA DC | **0.25mm** | R6/R7 output → C13/C14 → J3 |
| `XLR_R_HOT`, `XLR_R_COLD` | audio + 7mA DC | **0.25mm** | R8/R9 output → C15/C16 → J4 |
| `J4_L+`, `J4_L-`, `J4_R+`, `J4_R-` | audio signal | **0.25mm** | C13–C16 output → J2 (HiFiBerry) |
| `FBX` | µA | **0.2mm** | High-impedance — keep away from SW_NODE |
| `EN_UVLO`, `INTVCC`, `VC`, `VC_COMP` | µA–mA | **0.2mm** | Control/comp network |
| `SS`, `RT`, `SYNC_MODE`, `BIAS` | µA | **0.2mm** | Timing/mode |
| `SW_NODE` clearance to all others | — | **0.5mm** | Already enforced by DRC rule |

DRC minimums already encoded in `.kicad_dru`: 0.5mm power, 0.2mm signal.


## Critical Routing: SW_NODE

The switching node (U1 pins 14+16 → L1 pin 2 → D1 anode) is the primary source of
EMI. The enclosed loop area must be minimized.

**Route in this order:**
1. U1 pin 14 → U1 pin 16 (tie the two SW pins together, very short stub)
2. U1 SW → L1 pin 2 (1.5mm trace, as short as possible)
3. D1 anode → L1 pin 2 junction (keep D1 close to L1)
4. D1 cathode → C9 → +48V_RAW (1.5mm → 0.5mm after C9)

Do NOT route SW_NODE under the feedback network (R1/R2/C12/R3/C5).


## Boost Converter Input Loop

The second most important loop: J1 +5V → L2 → C6/C8 → U1 VIN.

- Route +5V_PI wide (1.0mm) from J1 pins 2+4 directly to L2 pin 1
- L2 pin 2 (+5V_FILT) fans out to: U1 pin 3, U1 pin 7, L1 pin 1, R5 pin 2, C1, C18
- C6 and C8 GND pins connect directly to the GND pour via short stubs — no long return traces


## Component Grouping and Routing Order

### Group 1: U1 decoupling (route first, before any other U1 connections)
These must be as close to U1 as possible and routed before long traces.
- **C17** (1µF INTVCC): pin 1 → U1 INTVCC (pin 5), pin 2 → GND pour
- **C18** (100nF BIAS): pin 1 → U1 BIAS (pin 7), pin 2 → GND pour
- **C2** (1µF VC): pin 1 → U1 VC (pin 8), pin 2 → GND pour
  - Then R4 and C4 in series for compensation: U1 VC → R4 → C4 → GND

### Group 2: Feedback network (route as a quiet island)
Keep these traces short and away from SW_NODE and L1/D1.
- R1 pin 1 → +48V_RAW, R1 pin 2 → FBX
- C12 pin 1 → +48V_RAW, C12 pin 2 → FBX (C12 is in parallel with R1)
- R2 pin 1 → FBX, R2 pin 2 → GND
- FBX → U1 pin 9 (short, direct)
- Keep the entire FBX island at x > 136, y = 70–74 (right of U1, away from L1/D1 side)

### Group 3: Timing, soft-start, mode (star-connect to GND pour)
- R3 (RT) → U1 pin 10, other end to GND
- C5 (SS) → U1 pin 11, other end to GND
- R11 (SYNC/MODE) → U1 pin 12, other end to GND
- R5 (EN/UVLO) → U1 pin 1, other end to +5V_FILT

### Group 4: Output filter chain
D1 cathode → +48V_RAW → C9 (bulk) → FB1 → +48V → C3/C7/C10/C11 (decoupling column)
Route as a left-to-right chain along the top of the output zone (y ≈ 56–65).
After FB1, the +48V rail runs through the output caps to SW1; R10 (LED) hangs off +48V_SW.

### Group 5: Phantom injection
+48V_SW (SW1 output) runs along the left edge to R6/R7/R8/R9.
- R6 → XLR_L_HOT → C13 → J4_L+ → J2 pin 5
- R7 → XLR_L_COLD → C14 → J4_L- → J2 pin 6
- R8 → XLR_R_HOT → C15 → J4_R+ → J2 pin 2
- R9 → XLR_R_COLD → C16 → J4_R- → J2 pin 1
- J3 pin 1 (GND), J3 pin 2 (XLR_L_HOT), J3 pin 3 (XLR_L_COLD)
- J4 pin 1 (GND), J4 pin 2 (XLR_R_HOT), J4 pin 3 (XLR_R_COLD)

The DC-block caps (C13–C16) sit between the bias resistors and the HiFiBerry connector (J2),
blocking 48V DC from reaching the HiFiBerry ADC inputs.


## GND Pour Notes

- GND zone is already defined on F.Cu. Press **B** in KiCad to fill before DRC.
- The 3×3 thermal via array under U1's exposed pad (EP, pin 17) connects F.Cu GND to B.Cu.
  These vias are essential for heat dissipation — do not remove or reduce them.
- Ensure the GND pour is unbroken under the feedback network (R1/R2/C12 area).
  A solid reference plane under FBX reduces noise pickup.
- GND stubs from C6, C8, C9 should connect directly into the pour (short, no meandering).


## Net Isolation Warnings

- **SW_NODE ↔ FBX**: Keep maximum physical separation. A coupling path here causes feedback
  instability and/or oscillation.
- **+48V → J2**: The DC-block caps (C13–C16) are the only protection keeping 48V off the
  HiFiBerry ADC inputs. Verify continuity of the DC-blocking path in DRC before assembly.
- **+5V_PI → +48V**: There must be no direct path. L2 and U1 are in between; confirm there
  is no accidental short via a via or polygon overlap.
- **GND on J3/J4 (XLR pin 1)**: This is the cable shield ground. Keep it connected to the
  board GND pour, but be aware that XLR cable shields can carry noise — consider whether to
  float or connect at the connector.


## Layer Strategy

All routing on F.Cu (top copper). Use B.Cu only for:
- J1 GPIO socket (already on B.Cu by design)
- GND stitching vias under U1 EP
- Optional: if traces become impossible to route on F.Cu, use vias to route a short segment on B.Cu

B.Cu should otherwise remain as a solid GND reference plane if a second copper pour is added.
