# Site de Swiped

Site d'une page, en 9 langues, pour l'app iOS Swiped (App Store id 6761209879). Il sert à être trouvé
et cité (Google, ChatGPT), à se distinguer des apps homonymes, et d'URL marketing pour la fiche.

- Textes : `content.py`, une entrée par langue, courts. Pas de sélecteur de langue : la racine envoie vers la langue du téléphone (`?lang=de` pour en forcer une).
- Génération : `python3 build.py`, qui écrit `index.html`, `fr/` … `zh/`, `sitemap.xml`, `robots.txt`, `llms.txt`.
- Aperçu : `python3 -m http.server 8000`, puis http://localhost:8000.
- Captures : celles de la fiche App Store, par langue (`img/shots/`). À remplacer quand la fiche change.
- Mesure : le bouton pointe vers un lien de campagne `ct=site`. Les téléchargements venus du site
  apparaissent dans App Store Connect, Analytics > Acquisition > Campagnes.
- Adresse : `BASE_URL` dans `build.py` (GitHub Pages `nicovlr.github.io/swiped/` par défaut).
