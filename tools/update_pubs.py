"""Rebuild publications.html from NASA ADS (refereed papers linked to the ORCID).

    python tools/update_pubs.py            # needs an ADS token in ~/.ads/dev_key or $ADS_TOKEN

ADS returns papers whose ORCID claim includes 0000-0002-1139-4880.  Papers missing from the list
can be added to the ORCID record (or claimed in ADS) and will appear on the next run.
"""
import html
import json
import os
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ORCID = "0000-0002-1139-4880"
ROOT = Path(__file__).resolve().parent.parent
FIELDS = "bibcode,title,author,year,pub,volume,page,doi,citation_count"


def token():
    t = os.environ.get("ADS_TOKEN")
    return t or (Path.home() / ".ads" / "dev_key").read_text().strip()


def query(q, rows=2000):
    url = "https://api.adsabs.harvard.edu/v1/search/query?" + urllib.parse.urlencode(
        {"q": q, "fl": FIELDS, "rows": rows, "sort": "date desc"})
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token()}"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["response"]["docs"]


def authors(a, me="Holman,"):
    """All authors up to 6; otherwise the first 3, plus MJH if later, and a count of the rest."""
    bold = lambda n: f"<b>{html.escape(n)}</b>" if n.startswith(me) else html.escape(n)
    if len(a) <= 6:
        return "; ".join(bold(n) for n in a)
    shown = [bold(n) for n in a[:3]]
    mine = next((i for i, n in enumerate(a) if n.startswith(me)), None)
    if mine is not None and mine >= 3:
        shown.append("… " + bold(a[mine]))
    return "; ".join(shown) + f"; and {len(a) - len(shown)} others"


def entry(d):
    title = html.escape((d.get("title") or [""])[0])
    link = f"https://ui.adsabs.harvard.edu/abs/{d['bibcode']}"
    ref = html.escape(d.get("pub", ""))
    if d.get("volume"):
        ref += f" {html.escape(d['volume'])}"
    if d.get("page"):
        ref += f", {html.escape(d['page'][0])}"
    return (f'<li><a href="{link}">{title}</a><br>'
            f'<span class="au">{authors(d.get("author", []))}</span><br>'
            f'<span class="ref">{ref} ({d["year"]})</span></li>')


def main():
    docs = query(f'orcid:"{ORCID}" property:refereed')
    by_year = {}
    for d in docs:
        by_year.setdefault(d["year"], []).append(entry(d))
    body = [f'<p class="note">{len(docs)} refereed papers, from '
            f'<a href="https://ui.adsabs.harvard.edu/search/q=orcid%3A%22{ORCID}%22">NASA ADS</a>, '
            f'updated {date.today():%-d %B %Y}.</p>']
    for y in sorted(by_year, reverse=True):
        body.append(f"<h2>{y}</h2>\n<ol class=\"pubs\">\n" + "\n".join(by_year[y]) + "\n</ol>")
    tpl = (ROOT / "tools" / "publications.tpl.html").read_text()
    (ROOT / "publications.html").write_text(tpl.replace("<!-- PUBLICATIONS -->", "\n".join(body)))
    print(f"{len(docs)} papers -> publications.html")


if __name__ == "__main__":
    main()
