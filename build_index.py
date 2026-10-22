#!/usr/bin/env python3
"""Build index.html from tests.json and add the back link to every page. Run before each commit.

Each tests.json entry: dir, page, title, desc (HTML), boy (Lexi/Brynjar), subject, created
(YYYY-MM-DDTHH:MM, Iceland time = UTC), optional print and updated.
"""
import json
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MONTHS = ["jan.", "feb.", "mars", "apr.", "maí", "júní", "júlí", "ágúst", "sept.", "okt.", "nóv.", "des."]
BOYS = ["Lexi", "Brynjar"]

tests = json.loads((ROOT / "tests.json").read_text())
for t in tests:
    for k in ("dir", "page", "title", "desc", "boy", "subject", "created"):
        assert t.get(k), (k, t)
    assert t["boy"] in BOYS, t
    for p in (t["page"], t.get("print")):
        assert p is None or (ROOT / p).is_file(), f"missing page {p}"
dirs = {p.parent.name for p in ROOT.glob("*/*.html")}
listed = {t["dir"] for t in tests}
assert dirs == listed, f"unlisted: {dirs - listed}, listed but missing: {listed - dirs}"


def stamp(iso):
    day, time = iso.split("T")
    y, m, d = day.split("-")
    return f"{int(d)}. {MONTHS[int(m) - 1]} {y} kl. {time}"


subjects = sorted({t["subject"] for t in tests})
tests.sort(key=lambda t: max(t["created"], t.get("updated", "")), reverse=True)

items = []
for t in tests:
    when = f"Búið til {stamp(t['created'])}" + (f" · uppfært {stamp(t['updated'])}" if t.get("updated") else "")
    prn = f' · <a href="{t["print"]}" style="font-size:.9rem">prentútgáfa</a>' if t.get("print") else ""
    items.append(
        f'  <li data-boy="{t["boy"]}" data-subject="{escape(t["subject"])}">'
        f'<span class="tags"><span>{t["boy"]}</span><span>{escape(t["subject"])}</span></span>'
        f'<a href="{t["page"]}">{t["title"]}</a>\n'
        f'      <small>{t["desc"]}{prn}</small><small class="when">{when}</small></li>')


def chips(name, values):
    return (f'<div class="chips" data-filter="{name}"><button type="button" data-v="" aria-pressed="true">Allt</button>'
            + "".join(f'<button type="button" data-v="{escape(v)}" aria-pressed="false">{escape(v)}</button>' for v in values)
            + "</div>")


page = f"""<!DOCTYPE html>
<html lang="is"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Æfingapróf</title>
<style>
  body{{font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;max-width:640px;margin:0 auto;padding:2.5rem 1.5rem;background:#fdfcf7;color:#1a1a1a;line-height:1.6}}
  h1{{color:#c8102e;margin-bottom:.2rem}} .sub{{color:#666;margin-top:0}}
  ul{{list-style:none;padding:0}} li{{background:#fff;border-left:4px solid #f6eb61;padding:1rem 1.2rem;margin:1rem 0;border-radius:0 4px 4px 0;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
  li[hidden]{{display:none}}
  a{{color:#c8102e;font-weight:600;text-decoration:none;font-size:1.1rem}} a:hover{{text-decoration:underline}}
  small{{display:block;color:#666;margin-top:.3rem}} small.when{{color:#999;font-size:.8rem;margin-top:.2rem}}
  .tags{{display:flex;gap:.4rem;margin-bottom:.3rem}} .tags span{{font-size:.75rem;background:#f4f1e6;color:#555;border-radius:999px;padding:0 .55rem}}
  .chips{{display:flex;flex-wrap:wrap;gap:.4rem;margin:.5rem 0}}
  .chips button{{font:inherit;font-size:.95rem;border:1px solid #ccc;background:#fff;border-radius:999px;padding:.25rem .9rem;cursor:pointer;color:#333}}
  .chips button[aria-pressed="true"]{{background:#c8102e;border-color:#c8102e;color:#fff}}
  #none{{color:#666}}
</style></head><body>
<h1>Æfingapróf</h1><p class="sub">Spegluð æfingapróf með földum svörum og orðaspjöld.</p>
{chips("boy", BOYS)}
{chips("subject", subjects)}
<ul>
{chr(10).join(items)}
</ul>
<p id="none" hidden>Ekkert próf passar við síuna.</p>
<script>
  const KEY = 'practice-exams-filter';
  let f = {{ boy: '', subject: '' }};
  try {{ const s = JSON.parse(localStorage.getItem(KEY)); if (s) f = Object.assign(f, s); }} catch (e) {{}}
  function apply() {{
    let shown = 0;
    document.querySelectorAll('li').forEach(li => {{
      const ok = (!f.boy || li.dataset.boy === f.boy) && (!f.subject || li.dataset.subject === f.subject);
      li.hidden = !ok; shown += ok;
    }});
    document.getElementById('none').hidden = shown > 0;
    document.querySelectorAll('.chips').forEach(g => g.querySelectorAll('button').forEach(b =>
      b.setAttribute('aria-pressed', String(b.dataset.v === f[g.dataset.filter]))));
    try {{ localStorage.setItem(KEY, JSON.stringify(f)); }} catch (e) {{}}
  }}
  document.querySelectorAll('.chips').forEach(g => g.addEventListener('click', e => {{
    const b = e.target.closest('button'); if (!b) return;
    f[g.dataset.filter] = b.dataset.v; apply();
  }}));
  apply();
</script>
</body></html>
"""
(ROOT / "index.html").write_text(page)
print(f"wrote index.html ({len(tests)} entries)")
sys.exit(subprocess.call([sys.executable, str(ROOT / "add_back_link.py")]))
