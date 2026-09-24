# Regam — site vitrine

Landing page de **Regam**, studio IA pour créer avatars, images 4K, vidéos animées et UGC ultra-réalistes.

Site 100 % statique (HTML/CSS/JS, aucune dépendance, aucun build).

## Lancer en local

```bash
cd regam
python3 -m http.server 8080
# puis ouvrir http://localhost:8080
```

## Structure

| Fichier       | Rôle                                                           |
|---------------|----------------------------------------------------------------|
| `index.html`  | Contenu : hero, fonctionnalités, studio démo, étapes, cas d'usage, tarifs, FAQ, CTA, footer |
| `styles.css`  | Design (tokens de couleurs en haut du fichier, responsive, animations) |
| `app.js`      | Menu mobile, prompt animé, studio démo, bascule mensuel/annuel, formulaire, animations au scroll |
| `favicon.svg` | Logo « R » Regam                                               |

## Personnaliser

- **Couleurs** : variables `--lime`, `--coral`, `--violet`, `--ink` dans `:root` (`styles.css`).
- **Tarifs** : attributs `data-m` (mensuel) / `data-y` (annuel) sur chaque prix.
- **Inscription** : le formulaire est une démo côté client — brancher `#signup` sur votre backend / outil d'e-mailing.
- **Visuels** : les portraits sont des dégradés + silhouette SVG ; remplacez-les par vos propres rendus IA.

## Déploiement

Glissez le dossier `regam/` sur Netlify, Vercel, GitHub Pages ou Cloudflare Pages.
