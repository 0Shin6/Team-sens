# Low Sens

Site officiel d'une structure e-sport, construit pour présenter son identité, ses équipes, ses actualités et ses compétitions. Le projet combine un site vitrine propulsé par **Astro** et deux services **Python** indépendants (une API **FastAPI** et un bot **Discord**) partageant une base de données SQLite en mode WAL.

## Aperçu

Le site propose plusieurs pages dédiées à la structure :

- accueil avec actualités et prochains matchs ;
- présentation de l'équipe et de son identité visuelle ;
- page roster (avec annonce d'arrivée prochaine) ;
- réseaux sociaux (avec compteurs de membres/abonnés en temps réel) et boutique ;
- formulaire de contact relié directement à Discord.

L'interface est responsive et intègre des données de secours permettant au site de rester 100 % fonctionnel (et prévisualisable sur GitHub Pages) lorsque l'API n'est pas joignable.

## Architecture (Option 1 — 2 services Python indépendants)

```text
Team-sens/
├── site/                    # Frontend Astro (composants, layouts, pages, styles)
├── backend/
│   ├── api/
│   │   ├── main.py          # Service 1 : API HTTP Python avec FastAPI
│   │   ├── socials.py       # Récupération asynchrone des statistiques réseaux
│   │   └── Dockerfile       # Conteneurisation de l'API
│   ├── bot/
│   │   ├── bot.py           # Service 2 : Bot Discord et commandes slash
│   │   └── Dockerfile       # Conteneurisation du Bot
│   └── requirements.txt     # Dépendances Python partagées
├── docker-compose.yml       # Orchestration des 2 services avec auto-restart
├── sens.fig                 # Maquette Figma du projet
└── .github/workflows/       # Vérification (tests + build) et déploiement GitHub Pages
```

### Site frontend (Astro)

Le frontend est développé avec **Astro** pour mutualiser la barre de navigation, le footer et les layouts tout en générant du HTML/CSS/JS statique ultra-léger. En développement, un proxy Vite redirige automatiquement `/api/*` vers `http://127.0.0.1:3000`.

### Service 1 : API backend (FastAPI)

L'API Python utilise **FastAPI**, **Uvicorn** et **SQLite (mode WAL)**. Elle fonctionne de manière totalement autonome du bot Discord (si le bot redémarre ou tombe, l'API continue de servir le site et d'envoyer les messages de contact via l'API REST Discord) :

| Méthode | Route | Rôle |
| --- | --- | --- |
| `GET` | `/api/health` | Vérifier l'état de santé de l'API |
| `GET` | `/api/news` | Récupérer les dernières actualités |
| `GET` | `/api/matches` | Récupérer les prochains matchs |
| `GET` | `/api/socials` | Récupérer les compteurs d'abonnés (Discord, Twitch, TikTok, X, YouTube) |
| `POST` | `/api/contact` | Envoyer un message privé Discord aux administrateurs |

### Service 2 : Bot Discord (`discord.py`)

Le bot Python permet d'administrer les données depuis Discord avec des commandes slash :

- ajouter, modifier, supprimer et afficher les matchs ;
- ajouter, supprimer et afficher les équipes ;
- ajouter et supprimer des actualités ;
- vérifier les équipes utilisées lors de la création d'un match.

Les données sont stockées dans une base SQLite partagée (`teamsens.db` en mode `WAL` pour permettre les lectures et écritures simultanées sans verrouillage).

## Technologies

- **Frontend** : Astro 5, HTML5, CSS3, JavaScript ;
- **Backend API** : Python, FastAPI, Uvicorn, aiohttp, SQLite (WAL) ;
- **Bot Discord** : Python, `discord.py`, `python-dotenv` ;
- **Infrastructure & CI/CD** : Docker Compose, GitHub Actions et GitHub Pages ;
- **Design** : Figma pour la conception de la maquette.

## Lancer le projet en local

### 1. Afficher le site (Astro)

Depuis le dossier `site` :

```bash
cd site
npm install
npm run dev
```

Puis ouvrir [http://localhost:4321](http://localhost:4321).

Pour générer la version de production statique (`site/dist`) :

```bash
npm run build
```

### 2. Installer l'environnement Python

Depuis la racine du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Créer `backend/.env` avec les variables nécessaires :

```env
token_discord=VOTRE_TOKEN_DISCORD
discord_recip=ID_DISCORD_1,ID_DISCORD_2
```

### 3. Lancer l'API FastAPI (Service 1)

```bash
.venv/bin/uvicorn backend.api.main:app --reload --port 3000
```

L'API démarre sur `http://127.0.0.1:3000` (documentation interactive disponible sur `http://127.0.0.1:3000/docs`).

### 4. Lancer le Bot Discord (Service 2)

```bash
.venv/bin/python backend/bot/bot.py
```

### Alternative : Lancer les 2 services avec Docker Compose (Production)

Les deux services tournent dans des conteneurs séparés avec `restart: unless-stopped` et partagent le volume SQLite :

```bash
docker compose up -d --build
```

## Tests

Les suites de tests unitaires des deux services Python peuvent être lancées depuis la racine du projet :

```bash
.venv/bin/python -m unittest discover -s backend/bot -p 'test_*.py'
.venv/bin/python -m unittest discover -s backend/api -p 'test_*.py'
```

## CI/CD

Le workflow [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) s'exécute sur les pull requests et les pushs vers `master`.

Il :

1. vérifie la compilation statique du site Astro (`npm run build`) ;
2. exécute les tests unitaires du bot Discord et de l'API FastAPI ;
3. publie automatiquement le rendu statique (`site/dist`) sur GitHub Pages après un push validé sur `master`.

Pour activer la publication, choisir **GitHub Actions** comme source dans `Settings > Pages` du dépôt GitHub.

## Objectif du projet

Ce projet m'a permis de travailler sur l'ensemble du cycle de création d'un produit web : recueil des besoins, conception sur Figma, intégration frontend, développement d'une API, stockage SQLite, automatisation via un bot Discord et mise en place d'une chaîne CI/CD. En plus de cela, cela permet à LowSens d'avoir un site complet fonctionnel et sur mesure avec la capacité de le mettre à jour sans passer par un développeur (pour les acutalités et les matchs)