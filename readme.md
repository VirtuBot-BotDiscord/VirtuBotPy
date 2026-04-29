# VirtuBot

Bot Discord modulaire (Python) avec commandes slash, moderation, jeux, tickets et panel web.

**Si vous cherchez la version privée, elle est disponible ici :**  
👉 https://virtubot.falous344.fr

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
git clone https://github.com/VirtuBot-BotDiscord/VirtuBotPy.git
cd VirtuBotPy
pip install -r requirements.txt
```

## Configuration .env

Cree un fichier .env a la racine du projet:


**Voici le .env d'exemple**

```env
#Exemple .env pour VirtuBotpy

# Discord bot
DISCORD_TOKEN=
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=


# Admin Panel - ID Discord de l'administrateur ayant accès au panel admin
# Pour obtenir votre ID: Paramètres Discord > Avancés > Mode développeur > Clic droit sur votre profil > Copier l'identifiant
ADMIN_USER_ID=

# Panel Web - Activer/désactiver le panel web
# true = Panel accessible normalement
# false = Mode maintenance (affiche page de maintenance)
PANEL_ENABLED=true

# Bot Status - Configuration du statut du bot
# Options: online, idle, dnd (do not disturb), invisible (offline)
BOT_STATUS=idle

# Bot Activity Type - Type d'activité à afficher : si vous voulez mettre le bot en mode stream, vous devez mettre BOT_ACTIVITY_TYPE sur "streaming"
# Options: game, streaming, watching, listening
BOT_ACTIVITY_TYPE=game

# Bot Activity - Texte de l'activité à afficher
BOT_ACTIVITY=VirtuBot | Semi open Source Bot

# Bot Streaming Config - Configuration du streaming
# true = Active le mode streaming avec URL
# false = Désactive le streaming
BOT_STREAMING_ENABLED=false

# Streaming URL - URL Twitch/YouTube pour le streaming
# Exemple: https://twitch.tv/votrechaine ou https://youtube.com/c/votrechannel
BOT_STREAMING_URL=https://twitch.tv/your_channel
```

## Configuration du Token Discord

Allez sur le Discord Developer Portal
Créez une nouvelle application
Allez dans l'onglet Bot
Cliquez sur Reset Token et copiez-le
Collez le token dans votre fichier .env
Important : Activez les Privileged Gateway Intents :

✅ Presence Intent
✅ Server Members Intent
✅ Message Content Intent

## Configuration du panel web (OAuth2 + Redirect URI)

Dans Discord Developer Portal:

- 1 Ouvre ton application Discord
- 2 Va dans OAuth2
- 3 Ajoute cette Redirect URI :

```text
http://localhost:3001/api/auth/callback
```

**Ne pas utiliser pour la production**

- 4 Sauvegarde

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

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment vous pouvez aider :

1. **Fork** le projet
2. Créez une **branche** pour votre fonctionnalité
3. **Commit** vos changements 
4. **Push** vers la branche 
5. Ouvrez une **Pull Request**

### Guidelines

- Suivez le style de code existant
- Commentez votre code en français
- Testez vos modifications avant de soumettre
- Mettez à jour la documentation si nécessaire



## 👥 Contributeurs

<div align="center">

### 🌟 Créé par

**[Falous-dev](https://github.com/Falous-dev)**

### 👥 Contributeurs

**[RomzyyTV](https://github.com/RomzyyTV)**
**[MilanDevpy](https://github.com/MilanDevpy)**
**[HdmDEV](https://github.com/HdmDEV)**

## Licence

Voir license.md

### 💡 Remerciements spéciaux

Merci à tous ceux qui contribuent à rendre **VirtuBot** meilleur chaque jour !



<sub>Made with ❤️ and Python | © 2026 VirtuBot Teams</sub>

</div>

