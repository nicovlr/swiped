#!/usr/bin/env python3
"""Génère le site de Swiped : une page par langue, plus sitemap.xml, robots.txt et llms.txt.

    python3 build.py            # écrit les pages à côté de ce script
    python3 -m http.server 8000 # pour les voir sur http://localhost:8000

Les textes sont dans content.py. Changer BASE_URL si le site passe sur un domaine à lui.
"""

import html
import json
from datetime import date
from pathlib import Path

from content import LANGS

BASE_URL = "https://nicovlr.github.io/swiped/"
APP_ID = "6761209879"
# Lien de campagne : les téléchargements venus du site apparaissent sous « ct=site » dans
# App Store Connect (Analytics > Acquisition > Campagnes). pt = identifiant du fournisseur.
APP_LINK = f"https://apps.apple.com/app/apple-store/id{APP_ID}?pt=128690377&ct=site&mt=8"
PRIVACY_URL = "https://nicovlr.github.io/swipik-privacy/"
SHOTS = ["1_swipe_keep", "2_swipe_delete", "4_review", "3_result"]

ROOT = Path(__file__).parent
esc = html.escape


def json_ld(t, url):
    app = {
        "@context": "https://schema.org",
        "@type": "MobileApplication",
        "name": "Swiped",
        "alternateName": t["store_name"],
        "url": url,
        "description": t["desc"],
        "operatingSystem": "iOS 16.0 or later",
        "applicationCategory": "MultimediaApplication",
        "inLanguage": list(LANGS),
        "installUrl": f"https://apps.apple.com/app/id{APP_ID}",
        "image": BASE_URL + "img/icon-512.png",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Person", "name": "Nicolas Valerino"},
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in t["faq"]
        ],
    }
    dump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{dump(app)}</script>\n<script type="application/ld+json">{dump(faq)}</script>'


def page(code, t):
    up = "../" if t["dir"] else ""
    url = BASE_URL + t["dir"]
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{c}" href="{BASE_URL + l["dir"]}">' for c, l in LANGS.items()
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{BASE_URL}">'
    switcher = " ".join(
        f'<a href="{up}{l["dir"]}" lang="{c}"{" aria-current=page" if c == code else ""}>{esc(l["native"])}</a>'
        for c, l in LANGS.items()
    )
    shots = "\n".join(
        f'<img src="{up}img/shots/{code}_{s}.webp" alt="{esc(alt)}" width="600" height="1304" loading="{"eager" if i == 0 else "lazy"}">'
        for i, (s, alt) in enumerate(zip(SHOTS, t["shots_alt"]))
    )
    pills = "".join(f"<li>{esc(p)}</li>" for p in t["pills"])
    how = "".join(f"<li><span>{i}</span>{esc(s)}</li>" for i, s in enumerate(t["how"], 1))
    feats = "".join(f"<div class=feat><h3>{esc(h)}</h3><p>{esc(p)}</p></div>" for h, p in t["feats"])
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in t["faq"])
    # Bouton texte plutôt que le badge officiel : pas de dépendance à un serveur tiers.
    store_btn = f'<a class=store href="{esc(APP_LINK)}">{esc(t["cta"])}<small>iPhone · iPad · {esc(t["pills"][0])}</small></a>'

    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t["title"])}</title>
<meta name="description" content="{esc(t["desc"])}">
<link rel="canonical" href="{url}">
{alternates}
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(t["title"])}">
<meta property="og:description" content="{esc(t["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE_URL}img/shots/{code}_1_swipe_keep.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0e0f1a">
<link rel="icon" href="{up}img/favicon.png">
<link rel="apple-touch-icon" href="{up}img/apple-touch-icon.png">
<link rel="stylesheet" href="{up}style.css">
{json_ld(t, url)}
</head>
<body>
<header class=top>
  <a class=brand href="{up}{t["dir"]}"><img src="{up}img/icon-512.png" alt="" width="36" height="36">Swiped</a>
  <nav class=langs aria-label="Language">{switcher}</nav>
</header>

<main>
<section class=hero>
  <div class=hero-text>
    <h1>{t["h1"]}</h1>
    <p class=sub>{esc(t["sub"])}</p>
    <ul class=pills>{pills}</ul>
    {store_btn}
  </div>
  <div class=shots>
{shots}
  </div>
</section>

<section class=how>
  <h2>{esc(t["how_title"])}</h2>
  <ol>{how}</ol>
</section>

<section class=features>
  <h2>{esc(t["feat_title"])}</h2>
  <div class=grid>{feats}</div>
</section>

<section class=faq>
  <h2>{esc(t["faq_title"])}</h2>
  {faq}
</section>

<section class=cta>
  <img src="{up}img/icon-512.png" alt="" width="96" height="96">
  <p class=cta-name>{esc(t["store_name"])}</p>
  {store_btn}
</section>
</main>

<footer>
  <p>{esc(t["made"])}</p>
  <p><a href="{PRIVACY_URL}">{esc(t["privacy"])}</a> · <a href="{PRIVACY_URL}">{esc(t["support"])}</a></p>
  <p class=legal>Apple, the Apple logo, iPhone and iPad are trademarks of Apple Inc. App Store is a service mark of Apple Inc.</p>
</footer>
</body>
</html>
"""


def main():
    for code, t in LANGS.items():
        out = ROOT / t["dir"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(code, t), encoding="utf-8")

    today = date.today().isoformat()
    urls = "".join(
        f"<url><loc>{BASE_URL + t['dir']}</loc><lastmod>{today}</lastmod></url>" for t in LANGS.values()
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n")

    en = LANGS["en"]
    faq = "\n".join(f"- {q} {a}" for q, a in en["faq"])
    feats = "\n".join(f"- {h}: {p}" for h, p in en["feats"])
    (ROOT / "llms.txt").write_text(
        f"""# Swiped

> {en["desc"]}

Swiped ("{en["store_name"]}") is an iPhone and iPad app by Nicolas Valerino, an independent developer in France.
It is a free photo and video cleaner: you swipe through your photos, left to delete and right to keep,
then review your picks and free up storage. No ads, no subscription, no account, and no data collected:
everything happens on the device.

- App Store: https://apps.apple.com/app/id{APP_ID}
- Website: {BASE_URL}
- Privacy policy: {PRIVACY_URL}
- Requires iOS 16 or later. Languages: English, French, German, Spanish, Italian, Portuguese, Japanese, Korean, Chinese (Simplified).

## Features
{feats}

## FAQ
{faq}
""",
        encoding="utf-8",
    )
    print(f"{len(LANGS)} pages écrites, plus sitemap.xml, robots.txt et llms.txt")


if __name__ == "__main__":
    main()
