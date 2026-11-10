#!/bin/sh
# One command: build every program this machine can build, time them, print one table.
#   sh run-all.sh /path/to/sutram_compiler [/path/to/a/second/sutram_compiler "its label"]
# Needs python3. Every other compiler is optional: a missing one leaves a row that says so.
set -e
cd "$(dirname "$0")"
if [ -z "$1" ]; then echo "usage: sh run-all.sh /path/to/sutram_compiler [second_compiler label]"; exit 2; fi
if [ -n "$2" ]; then
    python3 bench.py --sutram "$1" --sutram2 "$2" --label2 "${3:-Sutram (second compiler)}"
else
    python3 bench.py --sutram "$1"
fi
cat results.md
