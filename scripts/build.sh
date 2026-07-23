#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="trunk/Source/Scripts"
OUT="docs/visualizer.js"

mkdir -p docs

files=(
  "$SRC/dependencies/jquery-1.4.4.js"
  "$SRC/dependencies/jquery.address-1.3.1.min.js"
  "$SRC/dependencies/jquery.effects.core.js"
  "$SRC/dependencies/rdflib/util.js"
  "$SRC/dependencies/rdflib/uri.js"
  "$SRC/dependencies/rdflib/term.js"
  "$SRC/dependencies/rdflib/rdfparser.js"
  "$SRC/dependencies/rdflib/identity.js"
  "$SRC/visualizer.js"
  "$SRC/utils/htmlpopup.js"
  "$SRC/utils/rdfxmlparser.js"
  "$SRC/framework/core.js"
  "$SRC/framework/sandbox.js"
  "$SRC/modules/syncdataconnector.js"
  "$SRC/modules/schemaconnector.js"
  "$SRC/modules/dataservice.js"
  "$SRC/modules/schemaservice.js"
  "$SRC/modules/htmldrawservice.js"
  "$SRC/modules/historymanager.js"
  "$SRC/modules/cloudservice.js"
  "$SRC/modules/navigationservice.js"
  "$SRC/modules/animationservice.js"
  "$SRC/domain/node.js"
)

# Concatenate, stripping UTF-8 BOM (0xEF 0xBB 0xBF) from each file
for f in "${files[@]}"; do
  sed 's/\xef\xbb\xbf//g' "$f"
done > "$OUT"

echo "Built $OUT ($(wc -c < "$OUT") bytes)"
