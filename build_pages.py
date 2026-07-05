"""Wrap the artifact showcase.html into a standalone index.html for GitHub Pages.

The artifact form has no <!doctype>/<html>/<head>/<body> (the artifact host adds
them). GitHub Pages needs a full document, so we add a head with charset,
viewport, title, favicon, and a minimal reset — and drop the artifact's bare
<title> so it isn't duplicated.

    python build_pages.py
"""
import pathlib
import re

src = pathlib.Path("showcase.html").read_text()

m = re.search(r"<title>(.*?)</title>", src, flags=re.S)
title = m.group(1).strip() if m else "PayerLine"

# strip the leading bare <title> (artifact form); it moves into <head>
body = re.sub(r"^\s*<title>.*?</title>\s*", "", src, count=1, flags=re.S)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="PayerLine — an AI voice agent that verifies eligibility with a payer, catches the rep's mistakes, and routes only the risky calls to a human.">
<link rel="icon" href="data:image/svg+xml,&lt;svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'&gt;&lt;text y='.9em' font-size='90'&gt;📞&lt;/text&gt;&lt;/svg&gt;">
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{ margin: 0; }}
  img, svg, video {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

pathlib.Path("index.html").write_text(html)
print(f"wrote index.html ({len(html):,} bytes)  title={title!r}")
