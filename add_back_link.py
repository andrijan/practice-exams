#!/usr/bin/env python3
"""Put a "← Öll prófin" link back to index.html at the top of every page. Run before each commit; safe to re-run."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LINK = ('<a id="back-to-list" href="../index.html" style="display:inline-block;margin:10px 0 0 12px;'
        'padding:6px 14px;border-radius:999px;background:#fff;border:1px solid #ccc;color:#c8102e;'
        'font:600 15px -apple-system,\'Helvetica Neue\',Arial,sans-serif;text-decoration:none;'
        'position:relative;z-index:50">← Öll prófin</a>'
        '<style>@media print{#back-to-list{display:none!important}}</style>')

changed = 0
for page in sorted(ROOT.glob("*/*.html")):
    html = page.read_text()
    if 'id="back-to-list"' in html:
        continue
    new, n = re.subn(r"<body([^>]*)>", lambda m: m.group(0) + "\n" + LINK, html, count=1)
    if n != 1:
        raise SystemExit(f"no <body> in {page}")
    page.write_text(new)
    changed += 1
print(f"added the back link to {changed} page(s)")
