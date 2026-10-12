"""Wrap each page in src/ with the shared header, navigation and footer.

    python tools/build.py              # writes index.html, software.html, ... at the repo root
    python tools/update_pubs.py        # rebuilds publications.html from ADS (uses the same template)
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [("index", "Home"), ("publications", "Publications"), ("software", "Software"),
         ("talks", "Talks"), ("group", "Group"), ("cv", "CV")]


def page(name, title, body):
    cur = ' aria-current="page"'
    nav = "\n".join(
        f'    <a href="{p}.html"{cur if p == name else ""}>{t}</a>'
        for p, t in PAGES)
    head_title = "Matthew J. Holman" if name == "index" else f"{title} · Matthew J. Holman"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{head_title}</title>
<meta name="description" content="Matthew J. Holman, Senior Astrophysicist at the Smithsonian Astrophysical Observatory: solar system dynamics, orbit determination, and discovery of minor planets.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <p class="name"><a href="index.html">Matthew J. Holman</a></p>
  <p class="role">Senior Astrophysicist, Smithsonian Astrophysical Observatory · Center for Astrophysics | Harvard &amp; Smithsonian</p>
  <nav>
{nav}
  </nav>
</header>
<main>
{body}
</main>
<footer>Updated {date.today():%-d %B %Y}.</footer>
</body>
</html>
"""


def main():
    for name, title in PAGES:
        src = ROOT / "src" / f"{name}.html"
        if name == "publications":
            # template for tools/update_pubs.py, which fills <!-- PUBLICATIONS -->
            (ROOT / "tools" / "publications.tpl.html").write_text(
                page(name, title, "<h1>Publications</h1>\n<!-- PUBLICATIONS -->"))
            continue
        (ROOT / f"{name}.html").write_text(page(name, title, src.read_text().strip()))
    print("built", ", ".join(p for p, _ in PAGES if p != "publications"))


if __name__ == "__main__":
    main()
