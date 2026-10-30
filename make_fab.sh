#!/bin/sh
# Generate fabrication outputs into fab/ (gitignored): Gerbers + Excellon drill,
# pick-and-place CSV, and a zip for upload to JLCPCB / PCBWay / OSH Park.
# Runs DRC first and refuses to continue on any non-excluded violation.
set -eu
cd "$(dirname "$0")"

KCLI=${KCLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}
PCB=phantom-injector-hat.kicad_pcb
NAME=phantom-injector-hat
OUT=fab
REV=$(sed -n 's/.*(rev "\([^"]*\)").*/\1/p' "$PCB" | head -1)
mkdir -p "$OUT"

"$KCLI" pcb drc --schematic-parity --exit-code-violations --format report \
	-o "$OUT/drc.rpt" "$PCB" >/dev/null 2>&1 \
	|| { echo "DRC failed; see $OUT/drc.rpt" >&2; exit 1; }

rm -rf "$OUT/gerbers"
mkdir -p "$OUT/gerbers"

"$KCLI" pcb export gerbers --check-zones --subtract-soldermask \
	-l F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
	-o "$OUT/gerbers" "$PCB" 2>/dev/null
"$KCLI" pcb export drill --excellon-separate-th --generate-map --map-format pdf \
	-o "$OUT/gerbers" "$PCB" 2>/dev/null
"$KCLI" pcb export pos --side both --format csv --units mm --exclude-dnp \
	-o "$OUT/$NAME-pos.csv" "$PCB" 2>/dev/null
cp BOM.csv "$OUT/$NAME-BOM.csv"

rm -f "$OUT/$NAME-$REV-gerbers.zip"
(cd "$OUT/gerbers" && zip -q "../$NAME-$REV-gerbers.zip" ./*)

echo "Wrote $OUT/$NAME-$REV-gerbers.zip, $OUT/$NAME-pos.csv, $OUT/$NAME-BOM.csv"
