import discord
import os
import time
import asyncio
import json
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

print("📁 Démarrage du bot...")

latest_release = None

def read_version_file():
    """Lit la version depuis version.txt"""
    try:
        with open('version.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('Version='):
                    return line.split('=')[1].strip()
        return "V1.0.0"
    except Exception as e:
        print(f"⚠️ Erreur lecture version.txt: {e}")
        return "V1.0.0"

current_version = read_version_file()

def compare_versions(v1, v2):
    """Compare deux versions. Retourne 1 si v1 > v2, -1 si v1 < v2, 0 si égales"""
    def normalize_version(v):
        clean = v.upper().replace('V', '').strip()
        parts = clean.split('.')
        return [int(p) if p.isdigit() else 0 for p in parts]
    
    v1_parts = normalize_version(v1)
    v2_parts = normalize_version(v2)
    
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts += [0] * (max_len - len(v1_parts))
    v2_parts += [0] * (max_len - len(v2_parts))
    
    for i in range(max_len):
        if v1_parts[i] > v2_parts[i]:
            return 1
        elif v1_parts[i] < v2_parts[i]:
            return -1
    return 0

async def check_github_updates():
    """Vérifie les nouvelles releases sur GitHub"""
    global latest_release
    
    github_repo = 'VirtuBot-BotDiscord/VirtuBotPy'
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f'https://api.github.com/repos/{github_repo}/releases/latest'
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    latest_tag = data.get('tag_name', '').strip()
                    
                    if latest_tag:
                        comparison = compare_versions(current_version, latest_tag)
                        
                        if comparison < 0:
                            latest_release = {
                                'version': latest_tag,
                                'current_version': current_version,
                                'name': data.get('name', latest_tag),
                                'body': data.get('body', 'Aucune description'),
                                'url': data.get('html_url', ''),
                                'published_at': data.get('published_at', ''),
                                'download_url': data.get('zipball_url', ''),
                                'type': 'update_available'
                            }
                            
                            print(f"\n{'='*70}")
                            print(f"🔔 NOUVELLE MISE À JOUR DISPONIBLE !")
                            print(f"{'='*70}")
                            print(f"📌 Version actuelle : {current_version}")
                            print(f"✨ Nouvelle version : {latest_tag}")
                            print(f"📝 Titre           : {data.get('name', 'Sans titre')}")
                            print(f"🔗 Lien            : {data.get('html_url', '')}")
                            print(f"{'='*70}\n")
                            
                            update_file = 'config/update_info.json'
                            if not os.path.exists('config'):
                                os.makedirs('config')
                            with open(update_file, 'w', encoding='utf-8') as f:
                                json.dump(latest_release, f, indent=4, ensure_ascii=False)
                                
                        elif comparison > 0:
                            latest_release = {
                                'version': latest_tag,
                                'current_version': current_version,
                                'type': 'modified_version',
                                'name': 'Version non officielle',
                                'body': 'Vous utilisez une version modifiée',
                                'url': f'https://github.com/{github_repo}/releases'
                            }
                            
                            print(f"\n{'='*70}")
                            print(f"⚠️  ATTENTION : VERSION NON OFFICIELLE DÉTECTÉE")
                            print(f"{'='*70}")
                            print(f"📌 Version actuelle : {current_version}")
                            print(f"📦 Dernière release : {latest_tag}")
                            print(f"")
                            print(f"⚠️  Vous avez modifié le fichier version.txt")
                            print(f"❌ Vous ne serez plus averti des mises à jour officielles")
                            print(f"💡 Vous utilisez probablement une version de développement")
                            print(f"{'='*70}\n")
                            
                            update_file = 'config/update_info.json'
                            if not os.path.exists('config'):
                                os.makedirs('config')
                            with open(update_file, 'w', encoding='utf-8') as f:
                                json.dump(latest_release, f, indent=4, ensure_ascii=False)
                        else:
                            print(f"✅ Vous utilisez la dernière version ({current_version})")
                            update_file = 'config/update_info.json'
                            if os.path.exists(update_file):
                                os.remove(update_file)
                elif response.status == 404:
                    print(f"⚠️ Aucune release trouvée sur GitHub pour {github_repo}")
                else:
                    print(f"⚠️ Impossible de vérifier les mises à jour (Status: {response.status})")
    except aiohttp.ClientError as e:
        pass
    except Exception as e:
        pass

print("📁 Démarrage du bot...")

async def load_extensions():
    for extension in os.listdir('./cogs'):
        if extension.endswith('.py'):
            await bot.load_extension(f'cogs.{extension[:-3]}')
            if os.getenv("DEBUG_MODE").lower() == "true":
                print(f'Le module cogs.{extension[:-3]} a été chargé.')

@bot.event
async def on_ready():
    print(f'🤖 Votre bot {bot.user} est ONLINE.')
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║   ██╗   ██╗██╗██████╗ ████████╗██╗   ██╗██████╗  ██████╗ ████  ║
    ║   ██║   ██║██║██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔═══██╗╚██║  ║ 
    ║   ██║   ██║██║██████╔╝   ██║   ██║   ██║██████╔╝██║   ██║ ██║  ║
    ║   ╚██╗ ██╔╝██║██╔══██╗   ██║   ██║   ██║██╔══██╗██║   ██║ ██║  ║
    ║    ╚████╔╝ ██║██║  ██║   ██║   ╚██████╔╝██████╔╝╚██████╔╝ ██║  ║
    ║     ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝  ╚═╝  ║
    ║                                                                ║
    ║                       - Python -                               ║
    ║                   Open Source Discord Bot                      ║
    ║                       By falous344                             ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    time.sleep(5)
    print(f"{bot.user} est dans {len(bot.guilds)} serveurs.")
    
    bot_status = os.getenv("BOT_STATUS", "idle").lower()
    activity_type = os.getenv("BOT_ACTIVITY_TYPE", "game").lower()
    streaming_enabled = os.getenv("BOT_STREAMING_ENABLED", "false").lower() == "true"
    streaming_url = os.getenv("BOT_STREAMING_URL", "").strip()
    bot_activity_text = os.getenv("BOT_ACTIVITY", "VirtuBot")
    
    # Vérifier que l'URL est valide si le streaming est activé
    if streaming_enabled and (not streaming_url or streaming_url.endswith('/')):
        print(" URL de streaming invalide, streaming désactivé")
        streaming_enabled = False
    
    status_map = {
        "online": discord.Status.online,
        "idle": discord.Status.idle,
        "dnd": discord.Status.dnd,
        "invisible": discord.Status.invisible
    }
    status = status_map.get(bot_status, discord.Status.idle)
    
    activity = None
    if streaming_enabled and streaming_url:
        activity = discord.Streaming(name=bot_activity_text, url=streaming_url)
    elif activity_type == "streaming" and streaming_url:
        activity = discord.Streaming(name=bot_activity_text, url=streaming_url)
    elif activity_type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=bot_activity_text)
    elif activity_type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=bot_activity_text)
    else: 
        activity = discord.Game(name=bot_activity_text)
    
    await bot.change_presence(status=status, activity=activity)
    print(f" Statut: {bot_status} | Activité: {activity_type}" + (" | Streaming activé" if streaming_enabled else ""))
    
    try:
        await check_github_updates()
    except Exception as e:
        print(f"⚠️ Erreur vérification GitHub: {e}")
    
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} Commandes ont été chargées.")
    except Exception as e:
        print(e)
    
    try:
        from api.main import start_api_thread
        port = int(os.getenv('API_PORT', '3001'))
        start_api_thread(bot, port)
        print(f"✅ API démarrée sur http://localhost:{port}")
    except Exception as e:
        print(f"⚠️ Impossible de démarrer l'API: {e}")

async def main():
    async with bot:
        await load_extensions()
        
        BOT = os.getenv("DISCORD_TOKEN")
        if not BOT:
            print("❌ ERREUR: Variable DISCORD_TOKEN non définie!")
            print("Créez un fichier .env avec: DISCORD_TOKEN=votre_token")
            exit(1)
        await bot.start(BOT)

asyncio.run(main())

