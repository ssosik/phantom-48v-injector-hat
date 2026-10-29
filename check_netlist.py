#!/usr/bin/env python3
"""
Net-connectivity drift checker for phantom-injector-hat.

Compares the PCB's current net assignments against a saved golden snapshot.
Run after every "Update PCB from Schematic" (F8) to catch assignment drift.

Usage:
  python3 check_netlist.py           # compare PCB to golden (netlist_golden.json)
  python3 check_netlist.py --save    # save current PCB as the new golden reference
  python3 check_netlist.py --dump    # print current netlist and exit (no compare)

The golden file should be saved immediately after a clean F8 sync when the
schematic is known correct.  Re-save whenever you intentionally change the
schematic (new components, renamed nets, etc.).
"""

import os
import sys
import json
import argparse

sys.path.insert(0, (
    '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework'
    '/Versions/3.9/lib/python3.9/site-packages'
))
import pcbnew

HERE        = os.path.dirname(os.path.abspath(__file__))
PCB_PATH    = os.path.join(HERE, 'phantom-injector-hat.kicad_pcb')
GOLDEN_PATH = os.path.join(HERE, 'netlist_golden.json')

# Nets to ignore in the diff — these are KiCad's auto-generated names for
# pads that have no-connect flags in the schematic.  Their exact names can
# change across F8 runs without indicating real drift.
IGNORE_PREFIX = ('unconnected-',)


def extract_netlist(board):
    """Return {net_name: sorted list of 'REF:pad' strings}."""
    nets = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            net = pad.GetNetname()
            if not net:
                continue
            if any(net.startswith(p) for p in IGNORE_PREFIX):
                continue
            entry = f"{ref}:{pad.GetNumber()}"
            nets.setdefault(net, []).append(entry)
    for net in nets:
        nets[net].sort()
    return nets


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--save', action='store_true',
                        help='Save current PCB net assignments as the golden reference')
    parser.add_argument('--dump', action='store_true',
                        help='Print current netlist and exit')
    args = parser.parse_args()

    board = pcbnew.LoadBoard(PCB_PATH)
    current = extract_netlist(board)

    if args.dump:
        for net in sorted(current):
            print(f"{net}")
            for pad in current[net]:
                print(f"    {pad}")
        return

    if args.save:
        with open(GOLDEN_PATH, 'w') as f:
            json.dump(current, f, indent=2, sort_keys=True)
        total_pads = sum(len(v) for v in current.values())
        print(f"Saved golden: {len(current)} nets, {total_pads} pad assignments → {GOLDEN_PATH}")
        return

    try:
        with open(GOLDEN_PATH) as f:
            golden = json.load(f)
    except FileNotFoundError:
        print(f"No golden file found at {GOLDEN_PATH}")
        print("Run with --save after a clean 'Update PCB from Schematic' to create it.")
        sys.exit(1)

    all_nets = sorted(set(list(golden) + list(current)))
    drifted = []

    for net in all_nets:
        g = set(golden.get(net, []))
        c = set(current.get(net, []))
        missing = sorted(g - c)   # in golden but not in PCB → pad lost its net
        extra   = sorted(c - g)   # in PCB but not in golden → unexpected assignment
        if missing or extra:
            drifted.append((net, missing, extra))

    if not drifted:
        print(f"OK — {len(all_nets)} nets match golden. No drift detected.")
        return

    print(f"DRIFT DETECTED — {len(drifted)} net(s) changed:\n")
    for net, missing, extra in drifted:
        print(f"  {net}")
        for p in missing:
            print(f"    MISSING  {p}  ← pad lost its net (possible F8 regression)")
        for p in extra:
            print(f"    EXTRA    {p}  ← unexpected assignment (possible short or wrong net)")
    print()
    sys.exit(1)


if __name__ == '__main__':
    main()
