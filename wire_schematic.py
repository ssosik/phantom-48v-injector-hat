#!/usr/bin/env python3
"""
wire_schematic.py — Automate net wiring for phantom-injector-hat.kicad_sch

Removes all existing labels, no-connect flags, and power symbol instances,
then regenerates them from the verified netlist in this file.
Component placement is never touched.

Run from the project directory or with Python 3.8+.
Makes a .bak backup before writing.
"""

import re, math, uuid, shutil
from pathlib import Path

SCH = Path('/Users/stevesosik/Documents/KiCad/phantom-injector-hat/phantom-injector-hat.kicad_sch')

# ─── Pin connection-endpoint coords in symbol space (y-up convention) ──────────
LIB_PINS = {
    'Analog-Devices-LT8362-EMSE:LT8362EMSE-PBF': {
        '1': (0,0,0), '3': (0,-2.54,0), '5': (0,-5.08,0), '6': (0,-7.62,0),
        '7': (0,-10.16,0), '8': (0,-12.7,0),
        '9':  (55.88,-15.24,180), '10': (55.88,-12.7,180), '11': (55.88,-10.16,180),
        '12': (55.88,-7.62,180),  '14': (55.88,-5.08,180), '16': (55.88,-2.54,180),
        '17': (55.88,0,180),
    },
    'Device:R':           {'1':(0,3.81,270),  '2':(0,-3.81,90)},
    'Device:C':           {'1':(0,3.81,270),  '2':(0,-3.81,90)},
    'Device:L':           {'1':(0,3.81,270),  '2':(0,-3.81,90)},
    'Device:FerriteBead': {'1':(0,3.81,270),  '2':(0,-3.81,90)},
    'Device:LED':         {'1':(-3.81,0,0),   '2':(3.81,0,180)},
    'Diode:B260':         {'1':(-3.81,0,0),   '2':(3.81,0,180)},
    'Switch:SW_SPST':     {'1':(-5.08,0,0),   '2':(5.08,0,180)},
    # SPDT: pin 2 = common (left), pin 1 = top throw (right), pin 3 = bottom throw (right)
    'Switch:SW_SPDT':     {'1':(5.08,2.54,180), '2':(-5.08,0,0), '3':(5.08,-2.54,180)},
    'Connector_Generic:Conn_01x03': {
        '1':(-5.08,2.54,0), '2':(-5.08,0,0), '3':(-5.08,-2.54,0),
    },
    'Connector_Generic:Conn_02x03_Top_Bottom': {
        '1':(-5.08,2.54,0),  '2':(-5.08,0,0),  '3':(-5.08,-2.54,0),
        '4':(7.62,2.54,180), '5':(7.62,0,180), '6':(7.62,-2.54,180),
    },
    'Connector_Generic:Conn_02x20_Odd_Even': {
        # Odd pins 1,3,5,...,39 are in row 0,1,2,...,19 on the left side
        # Even pins 2,4,6,...,40 are in row 0,1,2,...,19 on the right side
        **{str(n): (-5.08, 22.86 - ((n-1)//2)*2.54, 0)   for n in range(1, 41, 2)},
        **{str(n): (7.62,  22.86 - ((n-2)//2)*2.54, 180) for n in range(2, 41, 2)},
    },
}

# ─── Netlist: (ref, pin_num_str) → net name or None (= no-connect) ─────────────
# Power-special nets: 'GND' → power:GND symbol; '+5V_PI' → power:+5V symbol
# All others → net label
J1_GND  = {'6','9','14','20','25','30','34','39'}
J1_5V   = {'2','4'}
J1_ALL  = {str(i) for i in range(1, 41)}
J1_NC   = J1_ALL - J1_GND - J1_5V

NETLIST = {
    ('U1','1'): 'EN_UVLO',  ('U1','3'): '+5V_FILT', ('U1','5'): 'INTVCC',
    ('U1','6'): None,        ('U1','7'): '+5V_FILT', ('U1','8'): 'VC',
    ('U1','9'): 'FBX',       ('U1','10'): 'RT',      ('U1','11'): 'SS',
    # Pin 12 = SYNC/MODE: 100kΩ to GND selects Burst+SSFM (low EMI, low idle current)
    ('U1','12'): 'SYNC_MODE', ('U1','14'): 'SW_NODE', ('U1','16'): 'SW_NODE',
    ('U1','17'): 'GND',

    ('L1','1'): '+5V_FILT',  ('L1','2'): 'SW_NODE',
    ('L2','1'): '+5V_PI',    ('L2','2'): '+5V_FILT',

    # D1 B260A: pin 2 = Anode → SW_NODE, pin 1 = Cathode → +48V_RAW
    ('D1','2'): 'SW_NODE',   ('D1','1'): '+48V_RAW',
    # FB1: pin 2 = input (+48V_RAW from D1 cathode), pin 1 = output (+48V clean)
    ('FB1','2'): '+48V_RAW', ('FB1','1'): '+48V',

    ('R1','1'): '+48V_RAW',  ('R1','2'): 'FBX',
    ('R2','1'): 'FBX',       ('R2','2'): 'GND',
    ('R3','1'): 'RT',        ('R3','2'): 'GND',
    ('R4','1'): 'VC',        ('R4','2'): 'VC_COMP',
    ('R5','1'): 'EN_UVLO',   ('R5','2'): '+5V_FILT',
    ('R6','1'): '+48V_SW',   ('R6','2'): 'XLR_L_HOT',
    ('R7','1'): '+48V_SW',   ('R7','2'): 'XLR_L_COLD',
    ('R8','1'): '+48V_SW',   ('R8','2'): 'XLR_R_HOT',
    ('R9','1'): '+48V_SW',   ('R9','2'): 'XLR_R_COLD',
    ('R10','1'): '+48V_SW',  ('R10','2'): 'LED_A',
    # R11: 100kΩ SYNC/MODE pull-down for Burst+SSFM mode
    ('R11','1'): 'SYNC_MODE', ('R11','2'): 'GND',

    ('C1','1'): '+5V_FILT',  ('C1','2'): 'GND',
    ('C2','1'): 'VC',        ('C2','2'): 'GND',
    ('C3','1'): '+48V',      ('C3','2'): 'GND',
    ('C4','1'): 'VC_COMP',   ('C4','2'): 'GND',
    ('C5','1'): 'SS',        ('C5','2'): 'GND',
    ('C6','1'): '+5V_PI',    ('C6','2'): 'GND',
    ('C7','1'): '+48V',      ('C7','2'): 'GND',
    ('C8','1'): '+5V_PI',    ('C8','2'): 'GND',
    ('C9','1'): '+48V_RAW',  ('C9','2'): 'GND',
    ('C10','1'): '+48V',     ('C10','2'): 'GND',
    ('C11','1'): '+48V',     ('C11','2'): 'GND',
    # C12 FBX feedforward cap (parallel with R1)
    ('C12','1'): '+48V_RAW', ('C12','2'): 'FBX',
    ('C13','1'): 'XLR_L_HOT', ('C13','2'): 'J4_L+',
    ('C14','1'): 'XLR_L_COLD',('C14','2'): 'J4_L-',
    ('C15','1'): 'XLR_R_HOT', ('C15','2'): 'J4_R+',
    ('C16','1'): 'XLR_R_COLD',('C16','2'): 'J4_R-',
    # C17: 1µF INTVCC bypass (required minimum per LT8362 datasheet)
    ('C17','1'): 'INTVCC',   ('C17','2'): 'GND',
    # C18: 100nF BIAS local bypass — +5V_FILT is the BIAS rail (same as U1 pin 7)
    ('C18','1'): '+5V_FILT', ('C18','2'): 'GND',

    # D2 LED (rot=270): pin 2=Anode (top), pin 1=Cathode (bottom)
    ('D2','2'): 'LED_A',     ('D2','1'): 'GND',

    # SPDT: pin 2 = common (output to bias resistors); pin 1 = +48V (ON), pin 3 = GND (OFF, actively drains rail)
    ('SW1','1'): '+48V',     ('SW1','2'): '+48V_SW',   ('SW1','3'): 'GND',

    ('J2','1'): 'J4_R-',  ('J2','2'): 'J4_R+',
    ('J2','3'): 'GND',    ('J2','4'): 'GND',
    ('J2','5'): 'J4_L+',  ('J2','6'): 'J4_L-',

    ('J3','1'): 'GND', ('J3','2'): 'XLR_L_HOT', ('J3','3'): 'XLR_L_COLD',
    ('J4','1'): 'GND', ('J4','2'): 'XLR_R_HOT', ('J4','3'): 'XLR_R_COLD',
}
for p in J1_GND: NETLIST[('J1', p)] = 'GND'
for p in J1_5V:  NETLIST[('J1', p)] = '+5V_PI'
for p in J1_NC:  NETLIST[('J1', p)] = None


# ─── Coordinate transform ───────────────────────────────────────────────────────
def pin_abs(sx, sy, sr, px, py):
    """Absolute schematic position of a pin endpoint.
    (sx,sy,sr) = symbol placement. (px,py) = pin in symbol space (y-up).
    KiCad schematic is y-down; symbol lib uses y-up.
    Formula: abs_x = sx + px·cos(θ) + py·sin(θ)
             abs_y = sy + px·sin(θ) − py·cos(θ)
    where θ is the component rotation in degrees (CCW in screen space).
    """
    rad = math.radians(sr)
    ax = sx + px * math.cos(rad) + py * math.sin(rad)
    ay = sy + px * math.sin(rad) - py * math.cos(rad)
    return round(ax, 4), round(ay, 4)


def label_angle(pin_sym_angle, comp_rot):
    """Label angle so text points away from the component body.
    pin_sym_angle: direction of pin stub INTO component in symbol space (degrees).
    comp_rot: component rotation (degrees CCW in screen).
    """
    a = (-pin_sym_angle - 180 + comp_rot) % 360
    # Round to nearest 90
    return int(round(a / 90) * 90) % 360


def justify(ang):
    return 'right bottom' if ang in (180, 270) else 'left bottom'


# ─── KiCad S-expression generators ─────────────────────────────────────────────
def new_uuid():
    return str(uuid.uuid4())


def gen_label(net, x, y, angle):
    j = justify(angle)
    return (
        f'\t(label "{net}"\n'
        f'\t\t(at {x} {y} {angle})\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t\t(justify {j})\n'
        f'\t\t)\n'
        f'\t\t(uuid "{new_uuid()}")\n'
        f'\t)\n'
    )


def gen_no_connect(x, y):
    return f'\t(no_connect (at {x} {y}) (uuid "{new_uuid()}"))\n'


PWR_COUNTER = [0]

def gen_power_symbol(lib_id, value, x, y, rot=0):
    """Generate a placed power symbol instance (GND or +5V)."""
    PWR_COUNTER[0] += 1
    ref = f'#PWR{PWR_COUNTER[0]:03d}'
    # For GND: Value shown above symbol; for +5V: below
    val_offset = -3.81 if lib_id == 'power:GND' else 3.81
    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x} {y} {rot})\n'
        f'\t\t(unit 1)\n'
        f'\t\t(body_style 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(in_pos_files yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(uuid "{new_uuid()}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f'\t\t\t(at {x} {y + val_offset} 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{value}"\n'
        f'\t\t\t(at {x} {y - val_offset} 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" ""\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" ""\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(pin "1"\n'
        f'\t\t\t(uuid "{new_uuid()}")\n'
        f'\t\t)\n'
        f'\t)\n'
    )


def gen_pwr_flag(x, y, net_lib_id):
    """PWR_FLAG suppresses power_pin_not_driven ERC for GND and +5V."""
    PWR_COUNTER[0] += 1
    ref = f'#PWR{PWR_COUNTER[0]:03d}'
    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "power:PWR_FLAG")\n'
        f'\t\t(at {x} {y} 0)\n'
        f'\t\t(unit 1)\n'
        f'\t\t(body_style 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(in_pos_files yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(uuid "{new_uuid()}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f'\t\t\t(at {x} {y - 2.54} 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "PWR_FLAG"\n'
        f'\t\t\t(at {x} {y + 2.54} 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(pin "1"\n'
        f'\t\t\t(uuid "{new_uuid()}")\n'
        f'\t\t)\n'
        f'\t)\n'
    )


# ─── New component injection ────────────────────────────────────────────────────
# Components that don't yet exist in the schematic and must be injected.
# Format: ref → (lib_id, x, y, rot, value, footprint, description)
PROJECT_PATH_UUID = '406c8d17-9b5b-489b-8b38-b913bdcb887d'

NEW_COMPONENTS = {
    # R11: 100kΩ from SYNC/MODE to GND → Burst+SSFM mode (low EMI, low idle current)
    # Placed to the right of U1 at SYNC/MODE pin y-level
    'R11': ('Device:R', 114.3, 185.42, 0,
            '100 kΩ 1%',
            'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder',
            'SYNC/MODE pull-down, selects Burst+SSFM'),
    # C17: 1µF INTVCC bypass — required minimum per LT8362 datasheet
    # INTVCC = 3.2V LDO output; placed to the left of U1 at INTVCC pin y-level
    'C17': ('Device:C', 33.02, 182.88, 0,
            '1 µF / 10V X7R',
            'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder',
            'INTVCC bypass, required minimum 1µF low ESR ceramic'),
    # C18: 100nF local bypass on BIAS pin (U1 pin 7) — datasheet recommends local
    # ceramic when BIAS is not connected to VOUT. Placed left of C17 at BIAS y-level.
    'C18': ('Device:C', 22.86, 187.96, 0,
            '100 nF / 10V X7R',
            'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder',
            'BIAS pin local bypass, 100nF ceramic per LT8362 datasheet'),
}


def gen_new_symbol(lib_id, ref, value, footprint, description, x, y, rot=0):
    """Generate a placed Device:R or Device:C symbol S-expression block."""
    if lib_id == 'Device:R':
        ref_dx, ref_dy = 2.54, -1.27
        val_dx, val_dy = 2.54,  1.27
        fp_x, fp_y, fp_rot = round(x - 1.778, 4), y, 90
    else:  # Device:C
        ref_dx, ref_dy = 3.81, -1.27
        val_dx, val_dy = 3.81,  1.27
        fp_x, fp_y, fp_rot = x, round(y + 3.81, 4), 0

    return (
        f'\n\t(symbol\n'
        f'\t\t(lib_id "{lib_id}")\n'
        f'\t\t(at {x} {y} {rot})\n'
        f'\t\t(unit 1)\n'
        f'\t\t(body_style 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(in_pos_files yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(fields_autoplaced yes)\n'
        f'\t\t(uuid "{new_uuid()}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f'\t\t\t(at {round(x+ref_dx,4)} {round(y+ref_dy,4)} 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(justify left)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{value}"\n'
        f'\t\t\t(at {round(x+val_dx,4)} {round(y+val_dy,4)} 0)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(justify left)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" "{footprint}"\n'
        f'\t\t\t(at {fp_x} {fp_y} {fp_rot})\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" ""\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Description" "{description}"\n'
        f'\t\t\t(at {x} {y} 0)\n'
        f'\t\t\t(hide yes)\n'
        f'\t\t\t(show_name no)\n'
        f'\t\t\t(do_not_autoplace no)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(pin "1"\n'
        f'\t\t\t(uuid "{new_uuid()}")\n'
        f'\t\t)\n'
        f'\t\t(pin "2"\n'
        f'\t\t\t(uuid "{new_uuid()}")\n'
        f'\t\t)\n'
        f'\t\t(instances\n'
        f'\t\t\t(project "phantom-injector-hat"\n'
        f'\t\t\t\t(path "/{PROJECT_PATH_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f'\t\t\t\t\t(unit 1)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
    )


# ─── Schematic parser ───────────────────────────────────────────────────────────
def find_block_end(text, start):
    """Return the index just past the closing ) of the S-expr block starting at start."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def extract_placed_components(content):
    """
    Returns (pre_text, list_of_component_blocks, closing_paren).
    pre_text = everything up to and including lib_symbols.
    component_blocks = each placed non-power symbol block, with leading whitespace.
    closing_paren = the root closing ')'.
    """
    # Find end of lib_symbols block
    ls_match = re.search(r'\(lib_symbols\b', content)
    ls_end = find_block_end(content, ls_match.start())

    # Everything up to and including lib_symbols
    pre = content[:ls_end]

    # Root closing paren is the last ')' in the file
    root_close_pos = len(content.rstrip()) - 1

    # Scan remaining content for top-level symbol blocks
    remaining = content[ls_end:root_close_pos]

    component_blocks = []
    pos = 0
    while pos < len(remaining):
        m = re.search(r'\(symbol\b', remaining[pos:])
        if not m:
            break

        abs_pos = pos + m.start()

        block_end = find_block_end(remaining, abs_pos)
        # Prepend the single-tab indent explicitly rather than scanning back
        # to line_start — scanning back would include leftover ')' from the
        # previous block on the same input line, accumulating on each run.
        block = '\t' + remaining[abs_pos:block_end]

        # Keep only real component instances (skip power:, GND_ symbols)
        lib_m = re.search(r'\(lib_id\s*"([^"]+)"', block)
        if lib_m:
            lib_id = lib_m.group(1)
            if not lib_id.startswith('power:') and not lib_id.startswith('GND_'):
                component_blocks.append(block)

        pos = block_end

    return pre, component_blocks, '\n)'


def get_placed_refs(content):
    """Extract all placed instances: {ref: (lib_id, sx, sy, sr)}

    Handles both KiCad single-line format:
      (symbol (lib_id "Foo:Bar") (at x y r) (unit 1) ...
    and script-injected multi-line format:
      (symbol
        (lib_id "Foo:Bar")
        (at x y r)
    """
    result = {}
    # \s* between tokens allows both " " (single-line) and "\n\t\t" (multi-line)
    pattern = (
        r'\(symbol\s*\(lib_id\s*"([^"]+)"\)\s*'
        r'\(at\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)\)'
        r'.*?\(property\s*"Reference"\s*"([^"]+)"'
    )
    for m in re.finditer(pattern, content, re.DOTALL):
        lib_id, sx, sy, sr, ref = m.groups()
        if not ref.startswith('#'):
            result[ref] = (lib_id, float(sx), float(sy), float(sr))
    return result


# ─── Main ────────────────────────────────────────────────────────────────────────
def main():
    content = SCH.read_text()

    # Backup
    bak = SCH.with_suffix('.kicad_sch.bak')
    shutil.copy(SCH, bak)
    print(f'Backed up to {bak}')

    # Parse
    pre, comp_blocks, post = extract_placed_components(content)
    placed = get_placed_refs(content)

    print(f'Found {len(placed)} placed component instances')

    # Inject new components not yet in the schematic
    new_sym_blocks = []
    for ref, (lib_id, x, y, rot, value, footprint, desc) in NEW_COMPONENTS.items():
        if ref not in placed:
            new_sym_blocks.append(gen_new_symbol(lib_id, ref, value, footprint, desc, x, y, rot))
            placed[ref] = (lib_id, x, y, rot)
            print(f'  Injecting new component: {ref} ({lib_id}) at ({x}, {y})')
        else:
            print(f'  Component {ref} already present, skipping injection')

    print(f'Netlist entries: {len(NETLIST)}')

    # Build connectivity elements
    labels = []
    no_connects = []
    power_syms = []

    # PWR_FLAG positions (place near J1)
    j1_info = placed.get('J1')

    for (ref, pin_num), net in NETLIST.items():
        if ref not in placed:
            print(f'  WARNING: {ref} not found in placed components, skipping')
            continue

        lib_id, sx, sy, sr = placed[ref]
        pin_defs = LIB_PINS.get(lib_id)
        if pin_defs is None:
            print(f'  WARNING: no pin defs for {lib_id} ({ref}), skipping')
            continue

        if pin_num not in pin_defs:
            print(f'  WARNING: pin {pin_num} not in {lib_id} defs for {ref}, skipping')
            continue

        px, py, p_sym_angle = pin_defs[pin_num]
        ax, ay = pin_abs(sx, sy, sr, px, py)
        la = label_angle(p_sym_angle, sr)

        if net is None:
            # No-connect flag
            no_connects.append(gen_no_connect(ax, ay))

        else:
            # Use net labels for all nets including GND and +5V_PI.
            # This avoids lib_symbol_mismatch and power_pin_not_driven ERC noise.
            labels.append(gen_label(net, ax, ay, la))

    # Assemble
    parts = [pre]
    parts.extend(comp_blocks)
    parts.extend(new_sym_blocks)
    parts.extend(labels)
    parts.extend(no_connects)
    parts.extend(power_syms)
    parts.append(post)

    new_content = ''.join(parts)
    SCH.write_text(new_content)

    print(f'Written: {SCH}')
    print(f'  Labels:       {len(labels)}')
    print(f'  No-connects:  {len(no_connects)}')
    print(f'  Power syms:   {len(power_syms)}')
    print(f'Total net entries placed: {len(labels) + len(no_connects) + len(power_syms)}')


if __name__ == '__main__':
    main()
