# Regam

Site de **Regam**, studio IA pour créer avatars, images 4K, vidéos animées et UGC ultra-réalistes.

- `public/` : le site (HTML/CSS/JS, sans build)
- `server.py` : serveur FastAPI qui sert le site et enregistre les inscriptions (SQLite)

## Lancer en local

```bash
cd regam
pip install -r requirements.txt
uvicorn server:app --reload --port 8080
# → http://localhost:8080
```

## API

| Méthode | Route          | Rôle |
|---------|----------------|------|
| GET     | `/api/health`  | Vérifie que le serveur tourne |
| POST    | `/api/signup`  | `{"email": "...", "plan": "decouverte" \| "createur" \| "pro"}` → `201` (nouvelle inscription) ou `200` avec `already: true` |

Protections : validation de l'e-mail, doublons ignorés (insensible à la casse), champ « pot de miel » anti-robots, limite de 5 requêtes/minute par IP (`REGAM_RATE_LIMIT`).

**Exporter les inscrits** :

```bash
python server.py export > inscriptions.csv
```

La base est stockée dans `data/regam.db` (modifiable via `REGAM_DB`), ignorée par git.

## Tests

```bash
pip install pytest httpx
python -m pytest tests
```

## Déploiement

**Docker** (Render, Railway, Fly.io, un VPS…) :

```bash
docker build -t regam .
docker run -p 8080:8080 -v regam-data:/data regam
```

**Hébergement statique seul** (Netlify, Vercel, GitHub Pages) : publiez le dossier `public/`. Le site fonctionne, mais sans serveur, le formulaire affiche « Les inscriptions ouvrent très bientôt ».

## Avant la mise en ligne

- Compléter les champs marqués **[à compléter]** dans `mentions-legales.html`, `cgu.html` et `confidentialite.html` (société, hébergeur, SIREN, médiateur…). Faites-les relire par un·e juriste.
- Remplacer `contact@regam.ai` par votre vraie adresse.
- Ajuster les tarifs (`data-m` / `data-y`) et les chiffres clés dans `index.html`.

## Personnaliser le design

Couleurs dans `:root` de `public/styles.css` : `--lime`, `--coral`, `--violet`, `--ink`. Polices : Unbounded (titres) et Inter (texte).
