#!/usr/bin/env python3
"""The book library chapters say four modules ship; twelve do. Correct the
claim in all six editions, in each edition's own language, and point to the
generated library reference instead of duplicating a table six times."""

EDITS = [
    ("docs/sutram-book-english.html",
     "Four modules ship today: math, num, sort and string.",
     "Twelve modules ship today, and the full list is in "
     "<code>docs/sutram-stdlib.html</code>."),

    ("docs/sutram-book-hindi.html",
     "आज के समय में चार मॉड्यूल्स उपलब्ध हैं: math, num, sort और string।",
     "आज बारह मॉड्यूल्स उपलब्ध हैं, और पूरी सूची "
     "<code>docs/sutram-stdlib.html</code> में है।"),

    ("docs/sutram-book-sanskrit.html",
     "अद्यत्वे चत्वारः विभागाः प्रेषिताः सन्ति: math, num, sort तथा string।",
     "अद्यत्वे द्वादश विभागाः सन्ति, पूर्णा सूची च "
     "<code>docs/sutram-stdlib.html</code> इत्यत्र अस्ति।"),

    ("docs/sutram-book-tamil.html",
     "இன்று நான்கு மாட்யூல்கள் கிடைக்கின்றன: math, num, sort மற்றும் string.",
     "இன்று பன்னிரண்டு மாட்யூல்கள் கிடைக்கின்றன; முழுப் பட்டியல் "
     "<code>docs/sutram-stdlib.html</code>-இல் உள்ளது."),

    ("docs/sutram-book-telugu.html",
     "ఈరోజు నాలుగు మాడ్యూల్స్ అందుబాటులో ఉన్నాయి: math, num, sort మరియు string.",
     "ఈరోజు పన్నెండు మాడ్యూల్స్ అందుబాటులో ఉన్నాయి; పూర్తి జాబితా "
     "<code>docs/sutram-stdlib.html</code> లో ఉంది."),

    ("docs/sutram-book-gujarati.html",
     "આજે ચાર મોડ્યુલ ઉપલબ્ધ છે: math, num, sort અને string.",
     "આજે બાર મોડ્યુલ ઉપલબ્ધ છે; સંપૂર્ણ યાદી "
     "<code>docs/sutram-stdlib.html</code> માં છે."),
]

for path, old, new in EDITS:
    s = open(path, encoding="utf-8").read()
    if old in s:
        open(path, "w", encoding="utf-8").write(s.replace(old, new, 1))
        print(f"  fixed  {path}")
    else:
        print(f"  MISS   {path}  (text not found verbatim)")
