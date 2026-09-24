# Regam

Site de **Regam**, studio IA pour créer avatars, images 4K, vidéos animées et UGC ultra-réalistes.

- `public/` : le site (HTML/CSS/JS, sans build)
- `server.py` : serveur FastAPI (site + API + base SQLite)
- `mailer.py` : e-mail de bienvenue (SMTP)
- `generate.py` : génération d'images IA via [fal.ai](https://fal.ai) (modèle FLUX)

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
| GET     | `/api/studio`  | `{"enabled": bool, "remaining": n}` : le studio est-il branché sur l'IA ? |
| POST    | `/api/generate`| `{"mode": "avatar"\|"image", "prompt", "style", "morpho", "ratio"}` → `{"url", "width", "height", "remaining"}` |

Protections : validation de l'e-mail, doublons ignorés (insensible à la casse), champ « pot de miel » anti-robots, limite de 5 requêtes/minute par IP (`REGAM_RATE_LIMIT`).

**Exporter les inscrits** :

```bash
python server.py export > inscriptions.csv
```

La base est stockée dans `data/regam.db` (modifiable via `REGAM_DB`), ignorée par git.

## Configuration (variables d'environnement)

Tout est optionnel : sans configuration, le site marche en mode démo.

### E-mail de bienvenue

Envoyé automatiquement à chaque **nouvelle** inscription (jamais en double). Compatible avec tout fournisseur SMTP (Brevo, Resend, Mailjet, OVH, Gmail…).

| Variable | Exemple |
|----------|---------|
| `SMTP_HOST` | `smtp-relay.brevo.com` |
| `SMTP_PORT` | `587` (défaut), ou `465` avec `SMTP_SSL=1` |
| `SMTP_USER` / `SMTP_PASSWORD` | identifiants SMTP |
| `SMTP_FROM` | `Regam <bonjour@regam.ai>` |
| `REGAM_SITE_URL` | `https://regam.ai` (lien dans l'e-mail) |

Un échec d'envoi est journalisé mais ne bloque jamais l'inscription.

### Studio IA (vraies images)

| Variable | Rôle |
|----------|------|
| `FAL_KEY` | Clé API fal.ai ([créer une clé](https://fal.ai/dashboard/keys)). **Sans clé, le studio reste en démo.** |
| `REGAM_FAL_MODEL` | Modèle, défaut `fal-ai/flux/schnell` (rapide, env. 0,003 $/image). Ex. `fal-ai/flux/dev` pour plus de qualité. |
| `REGAM_GEN_PER_IP_DAY` | Générations gratuites par visiteur (IP) et par jour, défaut `5` |
| `REGAM_GEN_DAILY_CAP` | Plafond global par jour, défaut `200` → **protège votre facture** |

Les modes **Avatar** et **Image** génèrent de vraies images ; **Vidéo** reste une démo en attendant les comptes et le paiement (une vidéo coûte bien plus cher). Les avatars sont toujours des personnes fictives, et le filtre de sécurité du modèle est activé.

Derrière un proxy ou un PaaS (Render, Railway…), les quotas par IP ont besoin de la vraie IP du visiteur : lancez uvicorn avec `--proxy-headers --forwarded-allow-ips='*'` **uniquement** si le serveur n'est joignable qu'à travers ce proxy.

## Tests

```bash
pip install pytest httpx
python -m pytest tests
```

## Déploiement

**Docker** (Render, Railway, Fly.io, un VPS…) :

```bash
docker build -t regam .
docker run -p 8080:8080 -v regam-data:/data \
  -e FAL_KEY=... -e SMTP_HOST=... -e SMTP_USER=... -e SMTP_PASSWORD=... \
  regam
```

**Hébergement statique seul** (Netlify, Vercel, GitHub Pages) : publiez le dossier `public/`. Le site fonctionne, mais sans serveur, le formulaire affiche « Les inscriptions ouvrent très bientôt ».

## Avant la mise en ligne

- Compléter les champs marqués **[à compléter]** dans `mentions-legales.html`, `cgu.html` et `confidentialite.html` (société, hébergeur, SIREN, médiateur…). Faites-les relire par un·e juriste.
- Remplacer `contact@regam.ai` par votre vraie adresse.
- Ajuster les tarifs (`data-m` / `data-y`) et les chiffres clés dans `index.html`.

## Personnaliser le design

Couleurs dans `:root` de `public/styles.css` : `--lime`, `--coral`, `--violet`, `--ink`. Polices : Unbounded (titres) et Inter (texte).
