# Regam

Studio IA pour créer avatars, images et vidéos : site vitrine, comptes, crédits, abonnements Stripe et génération réelle via fal.ai.

| Fichier | Rôle |
|---------|------|
| `public/` | Le site (HTML/CSS/JS, sans build) : accueil + studio, page **Mon compte**, pages légales |
| `server.py` | Serveur FastAPI : routes de l'API + service du site |
| `db.py` | Base SQLite : comptes, journal de crédits, générations |
| `auth.py` | Connexion sans mot de passe par lien magique, sessions |
| `mailer.py` | E-mails (SMTP) |
| `billing.py` | Abonnements Stripe (Checkout, espace client, webhooks) |
| `generate.py` | Images (FLUX) et vidéos (Kling) via fal.ai |

## Lancer en local

```bash
cd regam
pip install -r requirements.txt
REGAM_DEV=1 uvicorn server:app --reload --port 8080
# → http://localhost:8080
```

`REGAM_DEV=1` : sans SMTP, le lien de connexion s'affiche directement à l'écran (et dans le terminal). **Ne jamais l'activer en production.**

## Fonctionnement

**Comptes.** Pas de mot de passe : l'utilisateur saisit son e-mail et reçoit un lien valable 30 min, utilisable une seule fois. Le compte est créé au premier clic, avec **50 crédits offerts**. Session : cookie `HttpOnly`, `SameSite=Lax`, `Secure` en HTTPS, valable 30 jours.

**Crédits.** Image 1 · Avatar 2 · Vidéo 5 s 8 · Vidéo 10 s 16. Chaque mouvement est inscrit dans un journal ; une génération qui échoue est remboursée automatiquement.

**Visiteurs non connectés.** 5 essais d'image gratuits par jour et par IP, plafond global de 200 par jour. La vidéo nécessite un compte.

**Forfaits.**

| Forfait | Crédits | Vidéo |
|---------|---------|-------|
| Découverte (gratuit) | 50 à l'inscription | — |
| Créateur | 600 / mois (7 200 en annuel) | 5 s |
| Pro | 2 000 / mois (24 000 en annuel) | 5 s et 10 s |

Les crédits sont cumulables et conservés après résiliation. Changer de forfait passe par l'espace client Stripe (« Gérer mon abonnement ») : pas de double abonnement, et une montée en gamme ne crédite que la différence.

**Image → vidéo.** Après une image ou un avatar, « Animer cette image » passe en mode Vidéo avec l'image comme point de départ (aussi depuis la galerie de la page compte). Seules les créations de l'utilisateur peuvent être animées : jamais une URL ou une photo importée.

**Mode démo.** Sans `FAL_KEY`, ou si `public/` est hébergé seul, le studio affiche une animation de démonstration.

## Configuration (variables d'environnement)

### Général

| Variable | Rôle |
|----------|------|
| `REGAM_SITE_URL` | URL publique, ex. `https://regam.ai` (liens des e-mails, retours Stripe, cookie `Secure`) |
| `REGAM_DB` | Chemin de la base SQLite (défaut `data/regam.db`) |
| `REGAM_RATE_LIMIT` | Requêtes max par minute et par IP/e-mail (défaut 5) |

### E-mails (obligatoire pour la connexion en production)

| Variable | Exemple |
|----------|---------|
| `SMTP_HOST` | `smtp-relay.brevo.com` |
| `SMTP_PORT` | `587` (défaut), ou `465` avec `SMTP_SSL=1` |
| `SMTP_USER` / `SMTP_PASSWORD` | identifiants SMTP |
| `SMTP_FROM` | `Regam <bonjour@regam.ai>` |

### Génération IA (fal.ai)

| Variable | Rôle |
|----------|------|
| `FAL_KEY` | Clé API ([fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)) |
| `REGAM_FAL_MODEL` | Modèle image, défaut `fal-ai/flux/schnell` (~0,003 $/image) |
| `REGAM_FAL_VIDEO_MODEL` | Modèle texte → vidéo, défaut `fal-ai/kling-video/v1.6/standard/text-to-video` |
| `REGAM_FAL_I2V_MODEL` | Modèle image → vidéo, défaut `fal-ai/kling-video/v1.6/standard/image-to-video`. **Vérifiez les identifiants et prix actuels des modèles vidéo sur fal.ai** avant la mise en ligne. |
| `REGAM_GEN_PER_IP_DAY` | Essais gratuits par visiteur et par jour (défaut 5) |
| `REGAM_GEN_DAILY_CAP` | Plafond global d'essais gratuits par jour (défaut 200) |

⚠️ **Vérifiez vos marges** : 1 crédit est vendu environ 3 centimes (19 € / 600). Comparez avec le prix réel d'une vidéo chez fal.ai et ajustez `COSTS` dans `generate.py` si besoin.

### Stripe

1. Créez deux produits (Créateur, Pro) avec un prix mensuel récurrent (et annuel si voulu).
2. Renseignez :

| Variable | Rôle |
|----------|------|
| `STRIPE_SECRET_KEY` | `sk_test_…` puis `sk_live_…` |
| `STRIPE_PRICE_CREATEUR`, `STRIPE_PRICE_PRO` | IDs des prix mensuels (`price_…`) |
| `STRIPE_PRICE_CREATEUR_YEAR`, `STRIPE_PRICE_PRO_YEAR` | IDs des prix annuels (optionnels, sinon « Bientôt disponible ») |
| `STRIPE_WEBHOOK_SECRET` | `whsec_…` du webhook ci-dessous |

3. **Webhook** : Développeurs → Webhooks → endpoint `https://votre-domaine/api/stripe/webhook`, événements `invoice.paid` et `customer.subscription.deleted`.
4. **Espace client** : Paramètres → Billing → Customer portal → autorisez la résiliation et le changement de forfait entre vos deux produits.

Tester en local avec la CLI Stripe : `stripe listen --forward-to localhost:8080/api/stripe/webhook`.

### Derrière un proxy / PaaS

Les quotas par IP ont besoin de la vraie IP du visiteur : lancez uvicorn avec `--proxy-headers --forwarded-allow-ips='*'` **uniquement** si le serveur n'est joignable qu'à travers ce proxy.

## API

| Méthode | Route | Rôle |
|---------|-------|------|
| POST | `/api/auth/request` | `{email, plan?, next?}` → envoie le lien magique |
| POST | `/api/auth/verify` | `{token}` → ouvre la session (cookie) |
| POST | `/api/auth/logout` | Ferme la session |
| GET | `/api/me` · `/api/me/generations` | Compte, solde, historique |
| GET | `/api/studio` | État du studio (activé, coûts, essais restants, utilisateur) |
| POST | `/api/generate` | `{mode, prompt, style, morpho, ratio, duration}` → image, ou tâche vidéo |
| GET | `/api/jobs/{id}` | Suivi d'une vidéo (`pending` / `done` / `failed`) |
| GET | `/api/billing` | Formules disponibles |
| POST | `/api/billing/checkout` · `/api/billing/portal` | Redirection vers Stripe |
| POST | `/api/stripe/webhook` | Événements Stripe (signature vérifiée) |

Toutes les requêtes POST authentifiées exigent `Content-Type: application/json` (protection CSRF).

## Exporter les inscrits

```bash
python server.py export > inscriptions.csv
```

## Tests

```bash
pip install pytest httpx
python -m pytest tests
```

fal.ai, Stripe et SMTP sont simulés dans les tests : aucune clé nécessaire.

## Déploiement (Docker)

```bash
docker build -t regam .
docker run -p 8080:8080 -v regam-data:/data \
  -e REGAM_SITE_URL=https://regam.ai \
  -e SMTP_HOST=... -e SMTP_USER=... -e SMTP_PASSWORD=... -e SMTP_FROM="Regam <bonjour@regam.ai>" \
  -e FAL_KEY=... \
  -e STRIPE_SECRET_KEY=... -e STRIPE_WEBHOOK_SECRET=... -e STRIPE_PRICE_CREATEUR=... -e STRIPE_PRICE_PRO=... \
  regam
```

Le volume `/data` contient la base : **sauvegardez-le**. Une seule instance du serveur (SQLite) ; pour plusieurs instances, passer à PostgreSQL.

## Avant la mise en ligne

- Compléter les champs **[à compléter]** des pages légales (société, hébergeur, fournisseur d'e-mails, médiateur…) et les faire relire par un·e juriste — obligatoire avant d'encaisser des paiements.
- Remplacer `contact@regam.ai` par votre vraie adresse.
- Tester tout le parcours en mode test Stripe (`sk_test_…`, carte `4242 4242 4242 4242`).
- Relire les arguments marketing de la page d'accueil : certaines fonctions (Motion Control, voix, UGC produit, 4K) ne sont pas encore développées.
