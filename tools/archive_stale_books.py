#!/usr/bin/env python3
"""Replace superseded book editions with a short archive pointer to the
current editions.  Nothing is deleted from the project history; the old
files remain in the saved artifact archive.  This keeps any existing link
or bookmark working while removing content that had drifted."""
import os

CURRENT = [
    ("English",  "sutram-book-english.html"),
    ("हिन्दी",   "sutram-book-hindi.html"),
    ("संस्कृतम्", "sutram-book-sanskrit.html"),
    ("தமிழ்",    "sutram-book-tamil.html"),
    ("తెలుగు",    "sutram-book-telugu.html"),
    ("ગુજરાતી",  "sutram-book-gujarati.html"),
]

STALE = {
    "docs/sutram-book.html":       "the first English edition",
    "docs/sutram-book-2.html":     "an early English edition",
    "docs/sutram-book-3.html":     "an intermediate English edition",
    "books/sutram-book-indian.html": "a combined Hindi / Sanskrit / Telugu edition",
}

def page(title, was):
    rows = "\n".join(
        f'      <li><a href="{f}">{n}</a></li>' for n, f in CURRENT
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sutram — book editions</title>
<style>
  body {{ margin:0; padding:3rem 1.5rem; background:#0f1720; color:#dfe7ee;
         font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ max-width:44rem; margin:0 auto; }}
  h1 {{ color:#e86d11; font-size:1.5rem; margin:0 0 .25rem; }}
  p  {{ color:#9fb0c0; }}
  ul {{ list-style:none; padding:0; }}
  li {{ margin:.35rem 0; }}
  a  {{ color:#5fc7d6; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .note {{ border-left:3px solid #1a4a5c; padding-left:1rem; margin-top:2rem;
           font-size:.94rem; }}
</style>
</head>
<body>
<main>
  <h1>Sutram — the books</h1>
  <p>This page was {was}. It has been superseded by the current editions,
     which are kept in step with the language.</p>
  <ul>
{rows}
  </ul>
  <p class="note">The current editions each carry the full chapter set,
     including the chapter describing the present state of the language.
     Older editions were archived rather than kept in the tree, because
     duplicated copies drift out of step — which is exactly what had
     happened here.</p>
</main>
</body>
</html>
"""

for path, was in STALE.items():
    if os.path.exists(path):
        open(path, "w", encoding="utf-8").write(page("Sutram", was))
        print(f"  archived -> {path}")
    else:
        print(f"  (absent)   {path}")
