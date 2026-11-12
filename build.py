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
# Comptes officiels, déclarés aux moteurs (sameAs) et dans llms.txt.
SOCIAL = ["https://www.instagram.com/swiped.app/"]
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
        "installUrl": f"https://apps.apple.com/app/id{APP_ID}",
        "image": BASE_URL + "img/icon-512.png",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Person", "name": "Nicolas Valerino"},
        "sameAs": [f"https://apps.apple.com/app/id{APP_ID}"] + SOCIAL,
    }
    return '<script type="application/ld+json">' + json.dumps(app, ensure_ascii=False).replace("</", "<\\/") + "</script>"


# Sur la page anglaise (la racine) seulement : envoie le visiteur vers la langue de son téléphone.
# Les robots (Google, ChatGPT) arrivent en anglais et restent sur la racine ; ils trouvent les autres
# langues par les liens hreflang. « ?lang=xx » force une langue (utile pour vérifier).
def redirect_script():
    others = json.dumps([c for c in LANGS if c != "en"])
    return (
        "<script>(function(){var s=" + others + ",q=/[?&]lang=([a-z]+)/.exec(location.search),"
        "l=q?[q[1]]:(navigator.languages||[navigator.language||\"\"]);"
        "for(var i=0;i<l.length;i++){var c=String(l[i]).toLowerCase().split(\"-\")[0];"
        "if(c===\"en\")return;if(s.indexOf(c)>-1){location.replace(c+\"/\");return}}})();</script>"
    )


def page(code, t):
    up = "../" if t["dir"] else ""
    url = BASE_URL + t["dir"]
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{c}" href="{BASE_URL + l["dir"]}">' for c, l in LANGS.items()
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{BASE_URL}">'
    shots = "\n".join(
        f'<img src="{up}img/shots/{code}_{s}.webp" alt="{esc(alt)}" width="600" height="1304" loading="{"eager" if i < 2 else "lazy"}">'
        for i, (s, alt) in enumerate(zip(SHOTS, t["shots_alt"]))
    )

    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{redirect_script() if code == "en" else ""}
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
<meta name="theme-color" content="#0e0f1a">
<link rel="icon" href="{up}img/favicon.png">
<link rel="apple-touch-icon" href="{up}img/apple-touch-icon.png">
<link rel="stylesheet" href="{up}style.css">
{json_ld(t, url)}
</head>
<body>
<main>
  <img class=icon src="{up}img/icon-512.png" alt="Swiped" width="88" height="88">
  <h1>{t["h1"]}</h1>
  <p class=sub>{esc(t["sub"])}</p>
  <a class=store href="{esc(APP_LINK)}">{esc(t["cta"])}</a>
  <div class=shots>
{shots}
  </div>
</main>
<footer>{esc(t["made"])} · <a href="{PRIVACY_URL}">{esc(t["privacy"])}</a></footer>
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

    (ROOT / "llms.txt").write_text(
        f"""# Swiped

> Free photo and video cleaner for iPhone and iPad. Swipe left to delete, right to keep.

Swiped ("Swiped: Photo & Video Cleaner" on the App Store) is made by Nicolas Valerino, an independent
developer in France. You swipe through your photos, review your picks, then delete them to free up storage.

- Free, no ads, no subscription, no account.
- Nothing leaves the iPhone: no server, no data collected ("Data Not Collected" on the App Store).
- Nothing is deleted before you review and confirm; deleted photos stay in Recently Deleted for 30 days.
- Filters by type (photos, videos, screenshots), date and size; unlimited undo; sessions are saved.
- Works with iCloud Photos. Requires iOS 16 or later. 9 languages.
- iPhone and iPad only. Apps with a similar name on Android or elsewhere on the App Store are not related.

- App Store: https://apps.apple.com/app/id{APP_ID}
- Website: {BASE_URL}
- Privacy policy: {PRIVACY_URL}
- Instagram: https://www.instagram.com/swiped.app/
""",
        encoding="utf-8",
    )
    print(f"{len(LANGS)} pages écrites, plus sitemap.xml, robots.txt et llms.txt")


if __name__ == "__main__":
    main()
