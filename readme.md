<div align="center">

# 🤖 VirtuBot

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![Discord](https://img.shields.io/badge/Discord-Rejoindre-7289DA?logo=discord&logoColor=white)](https://discord.gg/2hXnp3std8)

**Un bot Discord moderne, modulaire et open-source 🚀**

_Fait par [Falous-dev](https://github.com/Falous-dev) _

![Commits](https://img.shields.io/github/commit-activity/m/Falous-dev/VirtuBot?style=flat-square&label=Commits)
![Last Commit](https://img.shields.io/github/last-commit/Falous-dev/VirtuBot?style=flat-square&label=Dernier%20commit)

[Installation](#-installation) • [Fonctionnalités](#-fonctionnalités) • [Configuration](#%EF%B8%8F-configuration) • [Commandes](#-commandes) • [Discord](https://discord.gg/2hXnp3std8)

---

</div>

# Ce readme Changera tres bientot !

## 📋 Description

**VirtuBot** est un bot Discord complet et personnalisable écrit en Python, conçu pour enrichir votre serveur avec des fonctionnalités de modération, de divertissement, et bien plus encore.

### ✨ Pourquoi VirtuBot ?

- 🎯 **Modulaire** : Architecture basée sur des Cogs pour une organisation claire
- 🔧 **Personnalisable** : Code ouvert et facilement modifiable
- 🎨 **Interface moderne** : Utilise les dernières fonctionnalités Discord (Slash Commands, Embeds, Buttons)
- 📦 **Sans base de données** : Utilise JSON pour une simplicité maximale

---

## 🌟 Fonctionnalités

### 🛡️ Modération

- **Kick/Ban** : Expulsion et bannissement avec notifications MP et raisons
- **Clear** : Suppression en masse de messages (1-100)
- **Timeout/Untimeout** : Exclusion temporaire (mute) des membres
- **Blacklist** : Système de bannissement automatique par serveur
- **Système de tickets** : Support client avec canaux privés et staff
- **Gestion des rôles** : Attribution de rôles de support pour les tickets

### 🎮 Divertissement

- **Jeux simples** : Pile ou face, dé, deviner un nombre, roulette russe
- **Quiz de culture** : Plus de 80 questions avec timer de 30 secondes
- **Puissance 4** : Jeu interactif avec système d'acceptation et timeout
- **Commandes utiles** : Say, embeds personnalisés, système de partenariats

### 🎫 Système de Tickets Avancé

- Création automatique de salons privés
- Canal staff séparé pour la coordination
- Boutons interactifs (Claim, Join, Priority, Transfer, Close)
- Archivage automatique des tickets fermés
- Statistiques utilisateurs et historique
- Multi-serveur : Configuration séparée par serveur

### 🔨 Système de Blacklist

- **Bannissement automatique** : Les utilisateurs blacklistés sont bannis dès qu'ils rejoignent
- **Par serveur** : Chaque serveur a sa propre blacklist indépendante
- **Persistant** : Même si l'utilisateur est débanni puis rejoint, il est rebanni automatiquement
- **Traçabilité** : Raisons enregistrées et logs détaillés

### 🔧 Configuration

- Configuration par serveur avec JSON
- Interface avec menus déroulants et boutons

---

## ⚠️ Clause de non-responsabilité

Ce projet est fourni **"tel quel"**, sans aucune garantie, explicite ou implicite.

L'auteur ne peut être tenu responsable des dommages, pertes de données, erreurs, pannes ou tout autre problème résultant de l'utilisation, de la mauvaise utilisation ou de la modification de ce code.

**En utilisant ce projet, vous acceptez l'entière responsabilité de son usage.**

---

## 🚀 Installation

### Prérequis

- **Python 3.14+** ([Télécharger](https://www.python.org/downloads/))
- **Git** ([Télécharger](https://git-scm.com/))
- **Un token Discord Bot** ([Guide](https://discord.com/developers/applications))

### Installation rapide

```bash
# 1. Cloner le repository
git clone https://github.com/Falous-dev/VirtuBot.git
cd VirtuBot

# 2. Exécuter le script d'installation
# Windows:
install.bat

# Linux/Mac:
chmod +x install.sh
./install.sh

# 3. Le bot démarre automatiquement après l'installation
```

**pas encore config!**

### Installation manuelle

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Créer le fichier .env
echo DISCORD_TOKEN=votre_token_ici > .env

# 3. Optionnel (Site Web) si vous voulez faire le système de panel admin

# 3. Lancer le bot
python main.py
```

### Configuration du Token Discord

1. Allez sur le [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez une nouvelle application
3. Allez dans l'onglet **Bot**
4. Cliquez sur **Reset Token** et copiez-le
5. Collez le token dans votre fichier `.env`

**Important :** Activez les **Privileged Gateway Intents** :

- ✅ Presence Intent
- ✅ Server Members Intent
- ✅ Message Content Intent

---

### Configuration du Site web

1. Allez sur le [Discord Developer Portal](https://discord.com/developers/applications)
2. Allez sur votre bot que vous avez créé
3. Allez dans l'onglet **OAuth2**
4. Ajouter un Redirect puis mettre votre IP/Nom De Domaine:3001/api/auth/callback
5. Puis, Save Change
---

## 🎯 Commandes

### 📌 Commandes de Base

| Commande | Description                                |
| -------- | ------------------------------------------ |
| `/help`  | Affiche la liste des commandes disponibles |
| `/hello` | Salue le bot et affiche la latence         |

### 🛠️ Modération

| Commande                        | Description                                     | Permissions requises |
| ------------------------------- | ----------------------------------------------- | -------------------- |
| `/kick <membre> [raison]`       | Expulse un membre du serveur                    | Expulser des membres |
| `/ban <membre> [raison]`        | Bannit un membre du serveur                     | Bannir des membres   |
| `/clear <nombre>`               | Supprime 1 à 100 messages dans le salon         | Gérer les messages   |
| `/timeout <membre> <durée>`     | Exclut temporairement un membre (mute)          | Modérer les membres  |
| `/untimeout <membre>`           | Retire l'exclusion temporaire d'un membre       | Modérer les membres  |
| `/blacklist <user_id> [raison]` | Ajoute un utilisateur à la blacklist du serveur | Administrateur       |

### 🎮 Jeux

| Commande                    | Description                                 |
| --------------------------- | ------------------------------------------- |
| `/jeux-pieces`              | Lance une pièce de monnaie (Pile ou Face)   |
| `/jeux-de`                  | Lance un dé à 6 faces                       |
| `/jeux-trouve-nombre`       | Devine un nombre entre 1 et 100             |
| `/jeux-roulette-russe`      | Joue à la roulette russe (1 chance sur 6)   |
| `/jeux-de-culture`          | Quiz de culture générale avec 80+ questions |
| `/puissance-4 <adversaire>` | Joue au Puissance 4 contre un autre joueur  |
| `/jeux-meme`                | Envoie un meme aléatoire                    |

### 🎫 Tickets

| Commande                                       | Description                                 | Permissions requises |
| ---------------------------------------------- | ------------------------------------------- | -------------------- |
| `/setup_ticket <channel> <category> [archive]` | Configure le système de tickets             | Gérer le serveur     |
| `/ticket_support_roles <action>`               | Gère les rôles de support (add/remove/list) | Gérer le serveur     |

### 🎨 Utilitaires

| Commande                                    | Description                      | Permissions requises |
| ------------------------------------------- | -------------------------------- | -------------------- |
| `/say <message>`                            | Fait parler le bot               | Gérer les messages   |
| `/sayembed <titre> <description> <couleur>` | Crée un embed personnalisé       | Gérer les messages   |
| `/partenariats`                             | Envoie un message de partenariat | Gérer le serveur     |

---

## ⚙️ Configuration

Le bot utilise des fichiers JSON pour stocker les configurations :

### Structure des fichiers

```
VirtuBot/
├── main.py                 # Point d'entrée du bot
├── config/                 # Fichiers de configuration
│   ├── ticket_config.json # Configuration des tickets par serveur
│   ├── ticket_data.json   # Données des tickets par serveur
│   ├── blacklist.json     # Liste des utilisateurs blacklistés par serveur
│   └── meme.json          # URLs des memes pour la commande /jeux-meme
├── api/                   # API Flask pour le panel
│   └── main.py           # Endpoints REST
├── panel/                 # Panel d'administration web
│   ├── index.html        # Page principale
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       ├── api.js        # Client API
│       └── app.js        # Logique application
├── cogs/                  # Modules du bot
│   ├── admin.py          # Commandes de modération + blacklist
│   ├── base.py           # Commandes de base
│   ├── games.py          # Jeux (simples + Puissance 4 + Quiz)
│   ├── ticket.py         # Système de tickets
│   └── tool.py           # Utilitaires
├── requirements.txt       # Dépendances Python
└── .env                  # Variables d'environnement (TOKEN)
```

### Configuration par serveur

Chaque serveur a sa propre configuration stockée avec son ID :

```json
{
  "123456789": {
    "ticket_channel": 987654321,
    "ticket_category": 111222333,
    "ticket_support_roles": [444555666],
    "archive_category": 777888999
  }
}
```

---

## � Panel d'Administration Web

VirtuBot dispose d'un panel web moderne pour gérer le bot à distance.

### 🚀 Démarrage du Panel

Le panel est une application web Flask accessible via navigateur :

```bash
# Lancer le panel (port 3001 par défaut)
python api/main.py
```

Accédez ensuite au panel via : **http://localhost:3001**

### ✨ Fonctionnalités du Panel

#### 📊 Tableau de Bord Principal (`index.html`)

- **Statistiques en temps réel** : Nombre de serveurs, utilisateurs, commandes exécutées
- **État du bot** : Latence, uptime, version
- **Graphiques** : Utilisation des commandes, activité par serveur
- **Actions rapides** : Redémarrage, synchronisation des commandes

#### 🔐 Authentification (`login.html`)

- Connexion sécurisée avec identifiant Discord
- Sessions persistantes
- Protection contre les accès non autorisés

#### 🖥️ Gestion des Serveurs (`serveur.html`)

- Liste de tous les serveurs où le bot est présent
- Configuration par serveur :
  - Système de tickets
  - Rôles de support
  - Catégories et canaux
  - Blacklist locale
- Statistiques détaillées par serveur

#### ⚠️ Logs et Erreurs (`errors.html`)

- **Logs des Commandes** : Historique complet avec filtres
- **Erreurs Récentes** : Codes d'erreur avec contexte
- **Documentation** : Guide de résolution intégré
- **Export** : Téléchargement des logs en JSON/CSV

### 🔧 Configuration de l'API

L'API Flask utilise les endpoints suivants :

| Endpoint                   | Méthode | Description                          |
| -------------------------- | ------- | ------------------------------------ |
| `/api/stats`               | GET     | Récupère les statistiques globales   |
| `/api/servers`             | GET     | Liste tous les serveurs              |
| `/api/servers/<id>`        | GET     | Détails d'un serveur spécifique      |
| `/api/servers/<id>/config` | PUT     | Met à jour la configuration          |
| `/api/blacklist`           | GET     | Liste des utilisateurs blacklistés   |
| `/api/blacklist/<id>`      | POST    | Ajoute un utilisateur à la blacklist |
| `/api/logs`                | GET     | Récupère les logs avec filtres       |
| `/api/commands/sync`       | POST    | Synchronise les commandes slash      |

### 🛠️ Développement du Panel

**Structure des fichiers :**

```
panel/
├── index.html          # Tableau de bord principal
├── login.html          # Page de connexion
├── serveur.html        # Gestion des serveurs
├── errors.html         # Logs et erreurs
├── css/
│   └── style.css      # Styles globaux (design moderne)
└── js/
    ├── api.js         # Client API (fetch, auth)
    └── app.js         # Logique application (interactivité)
    └── serveur.js     # Gestion serveurs (filtres, édition)
```

**Technologies utilisées :**

- **Backend** : Flask (Python) avec CORS
- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **Design** : Interface moderne avec thème sombre/clair
- **API** : REST avec JSON

### 🔒 Sécurité

- ⚠️ **Par défaut** : Le panel est accessible localement uniquement (`localhost:3001`)
- 🌐 **Production** : Configurez un reverse proxy (Nginx) avec HTTPS
- 🔑 **Authentification** : Implémentez OAuth2 Discord pour sécuriser l'accès
- 🛡️ **CORS** : Configurez les origines autorisées dans `api/main.py`

### 📝 Exemple de Configuration

```python
# api/main.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # À configurer pour la production

# Port personnalisé
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
```

---

## �🎨 Personnalisation

### Ajouter un nouveau module (Cog)

```python
# cogs/mon_module.py
import discord
from discord.ext import commands

bot = None

class MonModule(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance

        @bot.tree.command(name="ma-commande", description="Ma commande personnalisée")
        async def ma_commande(interaction: discord.Interaction):
            await interaction.response.send_message("Hello!")

async def setup(bot: commands.Bot):
    await bot.add_cog(MonModule(bot))
```

Le bot chargera automatiquement tous les fichiers `.py` du dossier `cogs/`.

---

## 🐛 Codes d'Erreur

VirtuBot utilise un système de codes d'erreur pour faciliter le débogage. Voici la liste complète :

### Codes d'Erreur Disponibles

| Code                  | Description               | Gravité          | Solution                                                                                                          |
| --------------------- | ------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| **ERR_PERMS**         | Permissions Insuffisantes | 🔴 Critique      | L'utilisateur ou le bot n'a pas les permissions nécessaires. Vérifiez les rôles et permissions du serveur.        |
| **ERR_ARGS**          | Argument Manquant         | 🟡 Avertissement | Une ou plusieurs valeurs requises n'ont pas été fournies. Consultez la documentation de la commande avec `/help`. |
| **ERR_CMD_NOT_FOUND** | Commande Introuvable      | 🔵 Info          | La commande demandée n'existe pas. Utilisez `/help` pour voir les commandes disponibles.                          |
| **ERR_COOLDOWN**      | Cooldown Actif            | 🟡 Avertissement | La commande a un temps de recharge. Attendez quelques secondes avant de réutiliser.                               |
| **ERR_UNKNOWN**       | Erreur Inconnue           | 🔴 Critique      | Erreur inattendue. Vérifiez les logs du bot pour plus de détails.                                                 |
| **ERR_API**           | Erreur API                | 🔴 Critique      | Impossible de communiquer avec l'API externe. Vérifiez la connexion internet et la configuration.                 |
| **ERR_DB**            | Erreur Base de Données    | 🔴 Critique      | Impossible d'accéder ou modifier les données. Vérifiez les fichiers de configuration JSON.                        |
| **ERR_TIMEOUT**       | Timeout                   | 🟡 Avertissement | L'opération a pris trop de temps et a été annulée. Réessayez plus tard.                                           |

### Logs et Monitoring

Le panel d'administration propose une page dédiée aux logs et erreurs :

- **Logs des Commandes** : Historique détaillé de toutes les commandes exécutées avec leurs paramètres
- **Erreurs Récentes** : Liste des erreurs avec codes, timestamps et contexte
- **Documentation** : Guide de résolution pour chaque code d'erreur

Accédez au panel via : `http://localhost:3001/errors.html`

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment vous pouvez aider :

1. **Fork** le projet
2. Créez une **branche** pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. **Commit** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

### Guidelines

- Suivez le style de code existant
- Commentez votre code en français
- Testez vos modifications avant de soumettre
- Mettez à jour la documentation si nécessaire

---

## 👥 Contributeurs

<div align="center">

### 🌟 Créé par

**[Falous-dev](https://github.com/Falous-dev)**

**[HDM](https://github.com/HdmDEV)**

### 💡 Remerciements spéciaux

Merci à tous ceux qui contribuent à rendre **VirtuBot** meilleur chaque jour !

---

<sub>Made with ❤️ and Python | © 2026 VirtuBot Teams</sub>

</div>
