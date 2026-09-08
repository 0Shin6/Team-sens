# Team Sens

Site officiel d'une structure e-sport, construit pour présenter son identité, ses équipes, ses actualités et ses compétitions. Le projet combine un site vitrine, une API Rust et un bot Discord pour administrer les données de la team.

## Aperçu

Le site propose plusieurs pages dédiées à la structure :

- accueil avec actualités et prochains matchs ;
- présentation de l'équipe et de son identité visuelle ;
- roster Valorant et profils des joueurs ;
- réseaux sociaux et boutique ;
- formulaire de contact relié à Discord.

L'interface est responsive et s'appuie sur des carrousels JavaScript pour afficher les actualités et les matchs. Des données de secours permettent également à la page d'accueil de rester utilisable lorsque l'API n'est pas disponible.

## Architecture

```text
Team-sens/
├── site/                 # Interface HTML, CSS, JavaScript et images
├── backend/
│   ├── src/main.rs       # API HTTP Rust avec Axum
│   └── bot/bot.py        # Bot Discord et commandes d'administration
├── sens.fig              # Maquette Figma du projet
└── .github/workflows/    # Vérification et déploiement GitHub Pages
```

### Site frontend

Le frontend est réalisé sans framework afin de garder une interface légère et facilement déployable. Il communique avec l'API pour récupérer les matchs et envoyer les messages du formulaire de contact.

### API backend

Le backend utilise Rust, Axum et SQLite. Il expose notamment :

| Méthode | Route | Rôle |
| --- | --- | --- |
| `GET` | `/api/news` | Récupérer les dernières actualités |
| `GET` | `/api/matches` | Récupérer les prochains matchs |
| `POST` | `/api/contact` | Envoyer un message vers Discord |

### Bot Discord

Le bot Python permet de gérer les données depuis Discord avec des commandes slash :

- ajouter, modifier, supprimer et afficher les matchs ;
- ajouter, supprimer et afficher les équipes ;
- ajouter et supprimer des actualités ;
- vérifier les équipes utilisées lors de la création d'un match.

Les données sont stockées dans une base SQLite partagée avec l'API.

## Technologies

- HTML5, CSS3 et JavaScript ;
- Rust 2024, Axum, Tokio et SQLx ;
- Python, `discord.py` et SQLite ;
- GitHub Actions et GitHub Pages ;
- Figma pour la conception de la maquette.

## Lancer le projet en local

### 1. Afficher le site

Depuis la racine du projet :

```bash
python3 -m http.server 8080 --directory site
```

Puis ouvrir [http://localhost:8080/acceuil.html](http://localhost:8080/acceuil.html).

Le frontend attend l'API à l'adresse `http://127.0.0.1:3000`.

### 2. Lancer l'API Rust

La base `teamsens.db` doit être disponible dans `backend/` avec les tables attendues par l'application.

```bash
cd backend
cargo run
```

L'API démarre sur `http://127.0.0.1:3000`.

### 3. Lancer le bot Discord

Installer les dépendances Python :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install discord.py python-dotenv
```

Créer `backend/.env` avec les variables nécessaires :

```env
token_discord=VOTRE_TOKEN_DISCORD
discord_recip=ID_DISCORD_1,ID_DISCORD_2
```

Puis lancer le bot :

```bash
python backend/bot/bot.py
```

Ne jamais publier le fichier `.env` ni le token du bot.

## Tests

Les tests peuvent être lancés séparément depuis la racine du projet :

```bash
cargo test --manifest-path backend/Cargo.toml
.venv/bin/python -m unittest discover -s backend/bot -p 'test_*.py'
```

Les tests Rust vérifient le format JSON envoyé au frontend. Les tests Python couvrent la normalisation des abréviations et les opérations principales sur les matchs et les équipes avec une base SQLite temporaire.

## CI/CD

Le workflow [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) s'exécute sur les pull requests et les pushs vers `master`.

Il :

1. vérifie la compilation du backend avec `cargo check` ;
2. vérifie la syntaxe du bot avec `py_compile` ;
3. publie automatiquement le dossier `site` sur GitHub Pages après un push validé sur `master`.

Pour activer la publication, choisir **GitHub Actions** comme source dans `Settings > Pages` du dépôt GitHub.

## Objectif du projet

Ce projet m'a permis de travailler sur l'ensemble du cycle de création d'un produit web : recueil des besoins, conception sur Figma, intégration frontend, développement d'une API, stockage SQLite, automatisation via un bot Discord et mise en place d'une chaîne CI/CD. En plus de cela, cela permet à LowSens d'avoir un site complet fonctionnel et sur mesure avec la capacité de le mettre à jour sans passer par un développeur (pour les acutalités et les matchs)