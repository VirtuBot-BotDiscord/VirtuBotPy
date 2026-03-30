# VirtuBot

Bot Discord modulaire (Python) avec commandes slash, moderation, jeux, tickets et panel web.

## Fonctionnalites principales

- Moderation: kick, ban, clear, timeout, untimeout, blacklist
- Tickets: systeme de support avec configuration par serveur
- Jeux: pile ou face, de, quiz, puissance 4, etc.
- Panel web: stats du bot, gestion serveurs, auth Discord OAuth2
- Stockage simple en JSON (pas de base de donnees)

## Prerequis

- Python 3.10+
- Un bot Discord (token)
- Dependances Python du fichier requirements.txt

## Installation rapide

```bash
git clone https://github.com/Falous-dev/VirtuBot.git
cd VirtuBot
pip install -r requirements.txt
```

## Configuration .env

Cree un fichier .env a la racine du projet:

```env
# Obligatoire
DISCORD_TOKEN=ton_token_bot

# Panel web / OAuth2 Discord
DISCORD_CLIENT_ID=client_id_application_discord
DISCORD_CLIENT_SECRET=client_secret_application_discord
ADMIN_USER_ID=ton_user_id_discord
PANEL_ENABLED=true
API_PORT=3001

# Optionnel (presence bot)
BOT_STATUS=idle
BOT_ACTIVITY_TYPE=game
BOT_ACTIVITY=VirtuBot
BOT_STREAMING_ENABLED=false
BOT_STREAMING_URL=

# Optionnel (logs de chargement des cogs)
DEBUG_MODE=false
```

## Configuration du panel web (OAuth2 + Redirect URI)

Dans Discord Developer Portal:

1. Ouvre ton application Discord
2. Va dans OAuth2
3. Ajoute cette Redirect URI:

```text
http://localhost:3001/api/auth/callback
```

4. Sauvegarde

Important:

- La Redirect URI dans Discord doit etre strictement identique a celle utilisee par l'API
- Le panel utilise API_PORT (3001 par defaut)
- Si tu changes le port, mets a jour la Redirect URI dans Discord

Exemple si port 5000:

```text
http://localhost:5000/api/auth/callback
```

## Lancer le bot + API panel

```bash
python main.py
```

Le bot lance aussi l'API Flask du panel sur:

```text
http://localhost:3001
```

## Problemes frequents

- Erreur OAuth2 redirect_uri mismatch:
  - Verifie la Redirect URI dans Discord Developer Portal
  - Verifie API_PORT dans .env
  - Redemarre le bot apres modification

- Impossible de se connecter au panel:
  - Verifie DISCORD_CLIENT_ID et DISCORD_CLIENT_SECRET
  - Verifie que PANEL_ENABLED=true
  - Verifie que l'API repond sur le bon port

- Token Discord invalide:
  - Verifie DISCORD_TOKEN dans .env

## Structure rapide

```text
main.py             # Demarrage bot + chargement cogs
api/main.py         # API Flask + OAuth2 + endpoints panel
cogs/               # Modules du bot
panel/              # Interface web
config/             # Fichiers JSON
requirements.txt    # Dependances Python
```

## Licence

Voir license.md
