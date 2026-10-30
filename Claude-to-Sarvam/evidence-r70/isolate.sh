#!/bin/sh
# R70: the brief's isolation table, re-run on v264 and v265, plus the controls that locate the cause
C264=$1; C265=$2; W=$3
t() { printf "$2" > $W/t.sm; for c in "$C264 v264" "$C265 v265"; do set -- $c; $1 $W/t.sm $W/t >/dev/null 2>&1 && r=$(timeout 1 $W/t | head -5 | tr '\n' ' ') || r="(refused)"; echo "  $2: $r"; done; }
echo "1. indented loop, nirmmita inside (the brief)"; t x 'mukhya()\n    vitti i = 0\n    yavat (i < 3)\n        likha("i=", i)\n        vitti p = nirmmita(64)\n        i = i + 1\n    likha("done")\n'
echo "2. the same with braces"; t x 'mukhya() {\n    vitti i = 0\n    yavat (i < 3) {\n        likha("i=", i)\n        vitti p = nirmmita(64)\n        i = i + 1\n    }\n    likha("done")\n}\n'
echo "3. indented loop, NO allocation (vitti q = i + 7 in its place)"; t x 'mukhya()\n    vitti i = 0\n    yavat (i < 3)\n        likha("i=", i)\n        vitti q = i + 7\n        i = i + 1\n    likha("done")\n'
echo "4. indented loop, two statements, nothing else"; t x 'mukhya()\n    vitti i = 0\n    yavat (i < 3)\n        likha("i=", i)\n        i = i + 1\n    likha("done")\n'
echo "5. indented loop, increment first"; t x 'mukhya()\n    vitti i = 0\n    yavat (i < 3)\n        i = i + 1\n        vitti q = 1\n        likha(i)\n    likha("done")\n'
