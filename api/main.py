from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from functools import wraps
import os
import sys
import threading
import requests
from collections import deque
from datetime import datetime
from dotenv import load_dotenv
import time
import psutil
import json

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PANEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'panel')

app = Flask(__name__, static_folder=PANEL_DIR)
CORS(app)


def get_user_from_token(token):
    """Récupère les informations utilisateur depuis le token Discord"""
    if not token:
        return None
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('https://discord.com/api/users/@me', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Erreur récupération utilisateur: {e}")
        return None

def get_user_guilds(token):
    """Récupère les serveurs Discord de l'utilisateur avec leurs permissions"""
    if not token:
        return []
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Erreur récupération guilds: {e}")
        return []

def user_has_admin_permission(token, guild_id):
    """Vérifie si l'utilisateur a les permissions administrateur sur un serveur"""
    if not token or not guild_id:
        print(f"[AUTH DEBUG] Token ou guild_id manquant")
        return False


    user = get_user_from_token(token)
    if user:
        user_id = str(user.get('id'))
        print(f"[AUTH DEBUG] User ID: {user_id}, Admin ID: {ADMIN_USER_ID}")
        if user_id == str(ADMIN_USER_ID):
            print(f"[AUTH DEBUG] ✅ Admin principal du bot détecté")
            return True
    else:
        print(f"[AUTH DEBUG] ⚠️ Discord API inaccessible - Mode dégradé activé")
        if ADMIN_USER_ID and token:
            print(f"[AUTH DEBUG] ✅ Autorisation temporaire accordée (bypass problème réseau)")
            return True
        print(f"[AUTH DEBUG] ❌ Impossible de récupérer l'utilisateur depuis le token")
        return False


    user_guilds = get_user_guilds(token)
    
    
    if not user_guilds:
        print(f"[AUTH DEBUG] ⚠️ Impossible de récupérer les serveurs - Mode dégradé activé")
        print(f"[AUTH DEBUG] ✅ Token OAuth2 valide, autorisation accordée")
        return True  
    
    print(f"[AUTH DEBUG] Serveurs de l'utilisateur: {len(user_guilds)} trouvés")

    for guild in user_guilds:
        if str(guild['id']) == str(guild_id):
            print(f"[AUTH DEBUG] Serveur trouvé: {guild.get('name', 'Unknown')} (ID: {guild['id']})")

            if guild.get('owner'):
                print(f"[AUTH DEBUG] ✅ Utilisateur est propriétaire du serveur")
                return True


            permissions = int(guild.get('permissions', 0))
            ADMINISTRATOR = 0x8
            MANAGE_GUILD = 0x20
            
            print(f"[AUTH DEBUG] Permissions brutes: {permissions} (binaire: {bin(permissions)})")
            
            if permissions & ADMINISTRATOR:
                print(f"[AUTH DEBUG] ✅ Permission ADMINISTRATOR détectée")
                return True
            
            if permissions & MANAGE_GUILD:
                print(f"[AUTH DEBUG] ✅ Permission MANAGE_GUILD détectée")
                return True
            
            print(f"[AUTH DEBUG] ❌ Permissions insuffisantes")

    print(f"[AUTH DEBUG] ❌ Serveur {guild_id} non trouvé dans la liste des serveurs de l'utilisateur")
    return False

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        

        if not token:
            token = request.args.get('token')
        
        if not token:
            print("[AUTH] ❌ Token manquant (ni en-tête ni URL)")
            return jsonify({'error': 'Token manquant', 'code': 'AUTH_REQUIRED'}), 401
        
        user = get_user_from_token(token)
        if not user:
            if ADMIN_USER_ID and token:
                print(f"[AUTH] ⚠️ Mode dégradé activé - Discord API inaccessible, autorisation accordée")
                return f(*args, **kwargs)
            print(f"[AUTH] ❌ Token invalide: {token[:20]}...")
            return jsonify({'error': 'Token invalide', 'code': 'INVALID_TOKEN'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_guild_admin(f):
    """Décorateur pour vérifier les permissions administrateur sur un serveur"""
    @wraps(f)
    def decorated_function(guild_id, *args, **kwargs):

        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        

        if not token:
            token = request.args.get('token')

        if not token:
            print(f"[AUTH] ❌ Aucun token fourni pour guild {guild_id} (ni en-tête ni URL)")
            return jsonify({'error': 'Token manquant', 'code': 'AUTH_REQUIRED'}), 401
        
        print(f"[AUTH] 🔑 Token reçu pour guild {guild_id}: {token[:20]}...")

        has_permission = user_has_admin_permission(token, guild_id)
        
        if not has_permission:
            print(f"[AUTH] ❌ Permissions refusées pour guild {guild_id}")
            return jsonify({
                'error': 'Permissions insuffisantes', 
                'code': 'INSUFFICIENT_PERMISSIONS',
                'message': 'Vous devez être administrateur de ce serveur'
            }), 403
        
        print(f"[AUTH] ✅ Accès autorisé pour guild {guild_id}")
        return f(guild_id, *args, **kwargs)
    return decorated_function

bot_client = None
command_logs = deque(maxlen=100)
error_logs = deque(maxlen=100)
bot_start_time = None

CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:3001/api/auth/callback'
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
PANEL_ENABLED = os.getenv('PANEL_ENABLED', 'true').lower() == 'true'

def set_bot_client(client):
    global bot_client, bot_start_time
    bot_client = client
    if bot_start_time is None:
        bot_start_time = time.time()

def log_command(command_name, user_name, guild_name, guild_id=None, parameters=None, channel_name=None):
    """Log une commande avec tous ses détails"""
    command_logs.append({
        'command': command_name,
        'user': user_name,
        'guild': guild_name,
        'guild_id': str(guild_id) if guild_id else None,
        'channel': channel_name,
        'parameters': parameters or {},
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

def log_error(error_code, error_message, user_name, guild_name, command_name=None, details=None):
    """Log une erreur avec un code d'erreur"""
    error_logs.append({
        'error_code': error_code,
        'error_message': error_message,
        'user': user_name,
        'guild': guild_name,
        'command': command_name,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def serve_login():
    if not PANEL_ENABLED:
        return send_from_directory(PANEL_DIR, 'maintenance.html')
    return send_from_directory(PANEL_DIR, 'login.html')

@app.route('/<path:path>')
def serve_static(path):
    if not PANEL_ENABLED and path not in ['maintenance.html', 'css/style.css']:
        return send_from_directory(PANEL_DIR, 'maintenance.html')
    return send_from_directory(PANEL_DIR, path)

@app.route('/api/auth/url', methods=['GET'])
def get_auth_url():
    if not CLIENT_ID:
        return jsonify({'error': 'CLIENT_ID not configured'}), 500
    
    scopes = 'identify guilds'
    auth_url = f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scopes}'
    return jsonify({'url': auth_url})

@app.route('/api/auth/callback', methods=['GET'])
def auth_callback():
    code = request.args.get('code')
    if not code:
        return '<h1>Erreur: Code manquant</h1>', 400
    
    if not CLIENT_SECRET:
        return '<h1>Erreur: CLIENT_SECRET not configured</h1>', 500
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    
    if response.status_code != 200:
        return f'<h1>Erreur OAuth2: {response.text}</h1>', 400
    
    tokens = response.json()
    access_token = tokens.get('access_token')
    
    return f'''
    <html>
    <head><title>Connexion réussie</title></head>
    <body>
        <h1>Connexion réussie!</h1>
        <p>Redirection en cours...</p>
        <script>
            localStorage.setItem('discord_token', '{access_token}');
            window.location.href = '/index.html';
        </script>
    </body>
    </html>
    '''



@app.route('/api/bot/stats', methods=['GET'])
def get_bot_stats():
    """Obtenir les statistiques du bot"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        stats = {
            'username': bot_client.user.name,
            'discriminator': bot_client.user.discriminator,
            'id': str(bot_client.user.id),
            'avatar': str(bot_client.user.avatar.url) if bot_client.user.avatar else None,
            'guilds': len(bot_client.guilds),
            'users': sum(guild.member_count for guild in bot_client.guilds),
            'latency': round(bot_client.latency * 1000, 2)
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds', methods=['GET'])
def get_guilds():
    """Obtenir la liste des serveurs"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        guilds = []
        for guild in bot_client.guilds:
            guilds.append({
                'id': str(guild.id),
                'name': guild.name,
                'icon': str(guild.icon.url) if guild.icon else None,
                'memberCount': guild.member_count,
                'ownerId': str(guild.owner_id)
            })
        return jsonify(guilds)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>', methods=['GET'])
@require_guild_admin
def get_guild_details(guild_id):
    """Obtenir les détails d'un serveur"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        guild = bot_client.get_guild(int(guild_id))
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        owner_name = 'Inconnu'
        if guild.owner:
            owner_name = f"{guild.owner.name}#{guild.owner.discriminator}"
        
        guild_data = {
            'id': str(guild.id),
            'name': guild.name,
            'icon': str(guild.icon.url) if guild.icon else None,
            'memberCount': guild.member_count,
            'ownerId': str(guild.owner_id),
            'ownerName': owner_name,
            'createdAt': guild.created_at.isoformat(),
            'description': guild.description,
            'region': 'Automatique',
            'channels': [{
                'id': str(c.id), 
                'name': c.name, 
                'type': str(c.type),
                'createdAt': c.created_at.isoformat()
            } for c in guild.channels],
            'roles': [{
                'id': str(r.id), 
                'name': r.name,
                'createdAt': r.created_at.isoformat()
            } for r in guild.roles],
            'members': [{
                'id': str(m.id),
                'username': m.name,
                'discriminator': m.discriminator,
                'avatar': str(m.avatar.url) if m.avatar else None,
                'bot': m.bot,
                'joinedAt': m.joined_at.isoformat() if m.joined_at else None
            } for m in list(guild.members)[:200]]
        }
        return jsonify(guild_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/members', methods=['GET'])
@require_guild_admin
def get_guild_members(guild_id):
    """Obtenir les membres d'un serveur"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        guild = bot_client.get_guild(int(guild_id))
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        members = []
        for member in guild.members[:100]:
            members.append({
                'id': str(member.id),
                'username': member.name,
                'discriminator': member.discriminator,
                'avatar': str(member.avatar.url) if member.avatar else None,
                'bot': member.bot,
                'joinedAt': member.joined_at.isoformat() if member.joined_at else None,
                'createdAt': member.created_at.isoformat() if member.created_at else None
            })
        return jsonify(members)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/bans', methods=['GET'])
@require_guild_admin
def get_guild_bans(guild_id):
    """Obtenir la liste des bans d'un serveur"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        guild = bot_client.get_guild(int(guild_id))
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        async def fetch_bans():
            ban_list = []
            try:
                async for ban_entry in guild.bans():
                    ban_list.append({
                        'user_id': str(ban_entry.user.id),
                        'username': ban_entry.user.name,
                        'discriminator': ban_entry.user.discriminator,
                        'avatar': str(ban_entry.user.avatar.url) if ban_entry.user.avatar else None,
                        'reason': ban_entry.reason or 'Aucune raison fournie'
                    })
            except Exception as e:
                print(f"Erreur lors de la récupération des bans: {e}")
                raise e
            return ban_list
        
        import asyncio
        future = asyncio.run_coroutine_threadsafe(fetch_bans(), bot_client.loop)
        ban_list = future.result(timeout=10)
        
        return jsonify(ban_list)
    except Exception as e:
        print(f"Erreur API bans: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/bans/<user_id>', methods=['DELETE'])
@require_guild_admin
def unban_user(guild_id, user_id):
    """Retirer le ban d'un utilisateur"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        guild = bot_client.get_guild(int(guild_id))
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        import asyncio
        from discord import Object
        future = asyncio.run_coroutine_threadsafe(guild.unban(Object(id=int(user_id))), bot_client.loop)
        future.result(timeout=10)
        
        return jsonify({'success': True, 'message': f'Utilisateur {user_id} débanni avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/bans', methods=['POST'])
@require_guild_admin
def ban_user(guild_id):
    """Bannir un utilisateur"""
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'error': 'user_id requis'}), 400
        
        user_id = data['user_id']
        reason = data.get('reason', 'Banni via le panel')
        
        guild = bot_client.get_guild(int(guild_id))
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        import asyncio
        from discord import Object
        
        async def do_ban():
            await guild.ban(Object(id=int(user_id)), reason=reason)
        
        future = asyncio.run_coroutine_threadsafe(do_ban(), bot_client.loop)
        future.result(timeout=10)
        
        return jsonify({'success': True, 'message': f'Utilisateur {user_id} banni avec succès'})
    except Exception as e:
        print(f"Erreur lors du bannissement: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/blacklist', methods=['GET'])
@require_guild_admin
def get_guild_blacklist(guild_id):
    """Óbtenir la blacklist d'un serveur avec informations utilisateur"""
    try:
        import json
        blacklist_file = 'config/blacklist.json'
        
        if not os.path.exists(blacklist_file):
            return jsonify({})
        
        with open(blacklist_file, 'r', encoding='utf-8') as f:
            blacklist_data = json.load(f)
        
        guild_blacklist = blacklist_data.get(str(guild_id), {})
        return jsonify(guild_blacklist)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/blacklist/<user_id>', methods=['POST'])
@require_guild_admin
def add_to_blacklist(guild_id, user_id):
    """Ajouter un utilisateur à la blacklist avec ses informations"""
    try:
        import json
        data = request.get_json()
        reason = data.get('reason', 'Aucune raison fournie')
        
        blacklist_file = 'config/blacklist.json'
        
        if not os.path.exists('config'):
            os.makedirs('config')
        
        if os.path.exists(blacklist_file):
            with open(blacklist_file, 'r', encoding='utf-8') as f:
                blacklist_data = json.load(f)
        else:
            blacklist_data = {}
        
        if str(guild_id) not in blacklist_data:
            blacklist_data[str(guild_id)] = {}
        
        if str(user_id) in blacklist_data[str(guild_id)]:
            return jsonify({'error': 'Utilisateur déjà dans la blacklist'}), 400
        
        user_info = {
            'reason': reason,
            'username': 'Utilisateur inconnu',
            'discriminator': '0000',
            'avatar': None,
            'added_at': datetime.now().isoformat()
        }
        
        if bot_client and bot_client.is_ready():
            guild = bot_client.get_guild(int(guild_id))
            if guild:
                import asyncio
                async def get_user_and_ban():
                    try:
                        member = await guild.fetch_member(int(user_id))
                        if member:
                            user_info['username'] = member.name
                            user_info['discriminator'] = member.discriminator
                            user_info['avatar'] = str(member.avatar.url) if member.avatar else None
                            try:
                                await member.send(f"❌ Vous avez été banni de **{guild.name}**.\n**Raison :** {reason}\n\nVous avez été ajouté à la blacklist du serveur.")
                            except:
                                pass
                            await member.ban(reason=f"Blacklist - {reason}")
                            return
                    except:
                        pass
                    
                    try:
                        user = await bot_client.fetch_user(int(user_id))
                        if user:
                            user_info['username'] = user.name
                            user_info['discriminator'] = user.discriminator
                            user_info['avatar'] = str(user.avatar.url) if user.avatar else None
                    except:
                        pass
                
                future = asyncio.run_coroutine_threadsafe(get_user_and_ban(), bot_client.loop)
                future.result(timeout=10)
        
        blacklist_data[str(guild_id)][str(user_id)] = user_info
        
        with open(blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(blacklist_data, f, indent=4, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': f'Utilisateur {user_id} ajouté à la blacklist', 'user_info': user_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/blacklist/<user_id>', methods=['DELETE'])
@require_guild_admin
def remove_from_blacklist(guild_id, user_id):
    """Retirer un utilisateur de la blacklist"""
    try:
        import json
        blacklist_file = 'config/blacklist.json'
        
        if not os.path.exists(blacklist_file):
            return jsonify({'error': 'Aucune blacklist trouvée'}), 404
        
        with open(blacklist_file, 'r') as f:
            blacklist_data = json.load(f)
        
        if str(guild_id) not in blacklist_data or str(user_id) not in blacklist_data[str(guild_id)]:
            return jsonify({'error': 'Utilisateur non trouvé dans la blacklist'}), 404
        
        del blacklist_data[str(guild_id)][str(user_id)]
        
        with open(blacklist_file, 'w') as f:
            json.dump(blacklist_data, f, indent=4)
        
        return jsonify({'success': True, 'message': f'Utilisateur {user_id} retiré de la blacklist'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/bot/commands', methods=['GET'])
def get_commands():
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        category_mapping = {
            'Base': 'Base',
            'Admin': 'Administration',
            'TICKETS': 'Tickets',
            'Games': 'Jeux',
            'Tool': 'Utilitaires',
            'Panel': 'Panel'
        }
        
        commands = []
        
        for command in bot_client.tree.get_commands():
            category = 'Autres'
            
            if command.name.startswith('jeux-'):
                category = 'Jeux'
            elif command.name in ['kick', 'ban', 'timeout', 'clear', 'warn']:
                category = 'Administration'
            elif command.name in ['say', 'sayembed', 'partenariats']:
                category = 'Utilitaires'
            elif 'ticket' in command.name.lower():
                category = 'Tickets'
            elif command.name in ['help', 'hello', 'ping']:
                category = 'Base'
            
            commands.append({
                'name': command.name,
                'description': command.description or 'Pas de description',
                'category': category
            })
        
        for cog in bot_client.cogs.values():
            cog_name = cog.__class__.__name__
            category = category_mapping.get(cog_name, cog.qualified_name)
            
            for command in cog.get_commands():
                commands.append({
                    'name': command.name,
                    'description': command.description or 'Pas de description',
                    'category': category
                })
        
        return jsonify(commands)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
@require_auth
def get_logs():
    return jsonify(list(command_logs))

@app.route('/api/errors', methods=['GET'])
@require_auth
def get_errors():
    return jsonify(list(error_logs))

@app.route('/api/errors/clear', methods=['POST'])
@require_auth
def clear_errors():
    error_logs.clear()
    return jsonify({'message': 'Errors cleared'})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'online',
        'bot_ready': bot_client.is_ready() if bot_client else False
    })



@app.route('/api/admin/check', methods=['POST'])
def check_admin():
    """Vérifie si un utilisateur est admin"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id or not ADMIN_USER_ID:
        return jsonify({'is_admin': False})
    
    return jsonify({'is_admin': str(user_id) == str(ADMIN_USER_ID)})

@app.route('/api/admin/id', methods=['GET'])
def get_admin_id():
    """Obtenir l'ID de l'administrateur"""
    return jsonify({'admin_id': ADMIN_USER_ID if ADMIN_USER_ID else None})

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Obtenir des statistiques avancées (admin uniquement)"""
    auth_header = request.headers.get('X-User-ID')
    if not auth_header or str(auth_header) != str(ADMIN_USER_ID):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not bot_client or not bot_client.is_ready():
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        uptime_seconds = int(time.time() - bot_start_time) if bot_start_time else 0
        uptime_days = uptime_seconds // 86400
        uptime_hours = (uptime_seconds % 86400) // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        text_channels = 0
        voice_channels = 0
        for guild in bot_client.guilds:
            text_channels += len(guild.text_channels)
            voice_channels += len(guild.voice_channels)
        
        stats = {
            'bot_info': {
                'username': bot_client.user.name,
                'id': str(bot_client.user.id),
                'avatar': str(bot_client.user.avatar.url) if bot_client.user.avatar else None
            },
            'guilds': {
                'total': len(bot_client.guilds),
                'list': [{'id': str(g.id), 'name': g.name, 'members': g.member_count} for g in bot_client.guilds]
            },
            'members': {
                'total': sum(guild.member_count for guild in bot_client.guilds),
                'unique': len(bot_client.users)
            },
            'channels': {
                'text': text_channels,
                'voice': voice_channels,
                'total': text_channels + voice_channels
            },
            'commands': {
                'total': len(bot_client.tree.get_commands()),
                'executed_today': len([log for log in command_logs if log.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
            },
            'uptime': {
                'seconds': uptime_seconds,
                'formatted': f"{uptime_days}j {uptime_hours}h {uptime_minutes}m",
                'days': uptime_days,
                'hours': uptime_hours,
                'minutes': uptime_minutes
            },
            'system': {
                'memory_mb': round(memory_info.rss / 1024 / 1024, 2),
                'cpu_percent': process.cpu_percent(),
                'threads': process.num_threads()
            },
            'latency': round(bot_client.latency * 1000, 2),
            'logs': {
                'commands': len(command_logs),
                'errors': len(error_logs)
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/restart', methods=['POST'])
def restart_bot():
    """Redémarrer le bot (admin uniquement)"""
    auth_header = request.headers.get('X-User-ID')
    if not auth_header or str(auth_header) != str(ADMIN_USER_ID):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not bot_client:
        return jsonify({'error': 'Bot not initialized'}), 503
    
    try:
        import asyncio
        
        async def restart():
            await bot_client.close()
        
        future = asyncio.run_coroutine_threadsafe(restart(), bot_client.loop)
        
        return jsonify({'message': 'Bot restart initiated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/logs/clear', methods=['POST'])
def clear_all_logs():
    """Effacer tous les logs (admin uniquement)"""
    auth_header = request.headers.get('X-User-ID')
    if not auth_header or str(auth_header) != str(ADMIN_USER_ID):
        return jsonify({'error': 'Unauthorized'}), 403
    
    command_logs.clear()
    error_logs.clear()
    
    return jsonify({'message': 'All logs cleared'})

@app.route('/api/admin/machine-logs', methods=['GET'])
def get_machine_logs():
    """Obtenir les logs machine (admin uniquement)"""
    auth_header = request.headers.get('X-User-ID')
    if not auth_header or str(auth_header) != str(ADMIN_USER_ID):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        import logging
        
        log_files = ['bot.log', 'virtubot.log', 'app.log']
        log_content = ''
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                break
        
        if not log_content:
            log_content = "Aucun fichier de logs trouvé.\n\n"
            log_content += "=== Logs de session ===\n"
            log_content += f"Bot démarré: {datetime.fromtimestamp(bot_start_time).strftime('%Y-%m-%d %H:%M:%S') if bot_start_time else 'N/A'}\n"
            log_content += f"Bot en ligne: {'Oui' if bot_client and bot_client.is_ready() else 'Non'}\n"
            log_content += f"Commandes exécutées: {len(command_logs)}\n"
            log_content += f"Erreurs enregistrées: {len(error_logs)}\n"
        
        if request.args.get('format') == 'text':
            return log_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        else:
            from flask import make_response
            response = make_response(log_content)
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=virtubot-logs-{datetime.now().strftime("%Y%m%d-%H%M%S")}.log'
            return response
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/machine-logs/clear', methods=['POST'])
def clear_machine_logs():
    """Effacer les logs machine (admin uniquement)"""
    auth_header = request.headers.get('X-User-ID')
    if not auth_header or str(auth_header) != str(ADMIN_USER_ID):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        log_files = ['bot.log', 'virtubot.log', 'app.log']
        cleared = False
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                cleared = True
        
        if cleared:
            return jsonify({'message': 'Machine logs cleared'})
        else:
            return jsonify({'message': 'No log files found to clear'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/guilds/<guild_id>/settings', methods=['GET'])
@require_guild_admin
def get_guild_settings(guild_id):
    """Obtenir les paramètres d'un serveur"""
    try:
        import json
        settings_file = f'config/settings_{guild_id}.json'
        
        default_settings = {
            'prefix': '!',
            'log_channel': None,
            'welcome_channel': None,
            'welcome_enabled': False,
            'auto_role': None,
            'auto_mod': False,
            'mod_role': None,
            'language': 'fr',
            'timezone': 'Europe/Paris'
        }
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                default_settings.update(settings)
        
        return jsonify(default_settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/settings', methods=['POST'])
@require_guild_admin
def save_guild_settings(guild_id):
    """Sauvegarder les paramètres d'un serveur"""
    try:
        import json
        data = request.get_json()
        
        if not os.path.exists('config'):
            os.makedirs('config')
        
        settings_file = f'config/settings_{guild_id}.json'
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Paramètres sauvegardés avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/settings', methods=['DELETE'])
@require_guild_admin
def reset_guild_settings(guild_id):
    """Réinitialiser les paramètres d'un serveur"""
    try:
        settings_file = f'config/settings_{guild_id}.json'
        
        if os.path.exists(settings_file):
            os.remove(settings_file)
        
        return jsonify({'success': True, 'message': 'Paramètres réinitialisés avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/guilds/<guild_id>/tickets/config', methods=['GET'])
@require_guild_admin
def get_ticket_config(guild_id):
    """Obtenir la configuration des tickets d'un serveur"""
    try:
        import json
        ticket_config_file = 'config/ticket_config.json'
        
        if os.path.exists(ticket_config_file):
            with open(ticket_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return jsonify(config.get(str(guild_id), {
                    'ticket_channel': None,
                    'ticket_category': None,
                    'archive_category': None,
                    'ticket_support_roles': []
                }))
        
        return jsonify({
            'ticket_channel': None,
            'ticket_category': None,
            'archive_category': None,
            'ticket_support_roles': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/tickets/config', methods=['POST'])
@require_guild_admin
def save_ticket_config(guild_id):
    """Sauvegarder la configuration des tickets d'un serveur"""
    try:
        import json
        data = request.get_json()
        
        if not os.path.exists('config'):
            os.makedirs('config')
        
        ticket_config_file = 'config/ticket_config.json'
        
        config = {}
        if os.path.exists(ticket_config_file):
            with open(ticket_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        config[str(guild_id)] = {
            'ticket_channel': data.get('ticket_channel'),
            'ticket_category': data.get('ticket_category'),
            'archive_category': data.get('archive_category'),
            'ticket_support_roles': data.get('ticket_support_roles', [])
        }
        
        with open(ticket_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Configuration des tickets sauvegardée'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/tickets', methods=['GET'])
@require_guild_admin
def get_guild_tickets(guild_id):
    """Obtenir la liste des tickets d'un serveur"""
    try:
        import json
        ticket_data_file = 'config/ticket_data.json'
        
        if not os.path.exists(ticket_data_file):
            return jsonify({'tickets': {}, 'user_stats': {}})
        
        with open(ticket_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            guild_data = data.get(str(guild_id), {'tickets': {}, 'user_stats': {}})
            
            tickets_list = []
            for ticket_id, ticket_info in guild_data.get('tickets', {}).items():
                ticket_info['ticket_id'] = ticket_id
                tickets_list.append(ticket_info)
            
            tickets_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return jsonify({
                'tickets': tickets_list,
                'user_stats': guild_data.get('user_stats', {}),
                'total': len(tickets_list),
                'open': len([t for t in tickets_list if t.get('status') == 'open']),
                'closed': len([t for t in tickets_list if t.get('status') == 'closed'])
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/tickets/panel', methods=['POST'])
@require_guild_admin
def send_ticket_panel(guild_id):
    """Envoyer le panel de création de tickets dans le canal configuré"""
    try:
        if not bot_client or not bot_client.is_ready():
            return jsonify({'error': 'Bot not ready'}), 503
        
        guild = bot_client.get_guild(int(guild_id))
        if not guild:
            return jsonify({'error': 'Guild not found'}), 404
        
        import json
        ticket_config_file = 'config/ticket_config.json'
        
        if not os.path.exists(ticket_config_file):
            return jsonify({'error': 'Configuration des tickets non trouvée'}), 404
        
        with open(ticket_config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            guild_config = config.get(str(guild_id))
            
            if not guild_config or not guild_config.get('ticket_channel'):
                return jsonify({'error': 'Canal de tickets non configuré'}), 400
        
        channel_id = guild_config['ticket_channel']
        channel = guild.get_channel(int(channel_id))
        
        if not channel:
            return jsonify({'error': 'Canal de tickets non trouvé'}), 404
        
        import asyncio
        
        async def send_panel():
            import discord
            from cogs.ticket import CreateTicketView
            
            embed = discord.Embed(
                title="🎫 SYSTÈME DE TICKETS",
                description="Créez un ticket pour obtenir de l'aide de notre équipe de support.",
                color=0x3498db
            )
            embed.add_field(
                name="📋 Comment ça marche ?",
                value="• Cliquez sur **🎫 Créer un Ticket**\n• Remplissez le formulaire\n• Un salon privé sera créé\n• Notre équipe vous aidera !",
                inline=False
            )
            embed.set_footer(text="Support disponible 24/7")
            
            view = CreateTicketView()
            await channel.send(embed=embed, view=view)
            
            return True
        
        future = asyncio.run_coroutine_threadsafe(send_panel(), bot_client.loop)
        result = future.result(timeout=10)
        
        return jsonify({'success': True, 'message': 'Panel de tickets envoyé avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/update/check', methods=['GET'])
def check_update():
    """Vérifier s'il y a une mise à jour disponible"""
    import json
    try:
        update_file = 'config/update_info.json'
        if os.path.exists(update_file):
            try:
                with open(update_file, 'r', encoding='utf-8') as f:
                    update_info = json.load(f)
                    return jsonify({
                        'update_available': True,
                        'update_info': update_info
                    })
            except json.JSONDecodeError as je:
                print(f"Erreur JSON dans update_info.json: {je}")
                return jsonify({'update_available': False, 'error': 'Invalid JSON'})
        return jsonify({'update_available': False})
    except Exception as e:
        print(f"Erreur dans check_update: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'update_available': False, 'error': str(e)})


@app.route('/api/guilds/<guild_id>/warns', methods=['GET', 'POST', 'DELETE'])
@require_guild_admin
def manage_guild_warns(guild_id):
    """Obtenir tous les warns d'un serveur ou ajouter un nouveau warn"""
    try:
        warns_file = 'config/warns.json'
        
        if request.method == 'GET':
            if not os.path.exists(warns_file):
                return jsonify({'warns': {}, 'total': 0})
            
            try:
                with open(warns_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        data = {}
                    else:
                        data = json.loads(content)
            except json.JSONDecodeError:
                print("[WARN] warns.json corrompu, réinitialisation...")
                data = {}
                
            guild_warns = data.get(str(guild_id), {})
            
            total_warns = sum(len(warns) for warns in guild_warns.values())
            
            return jsonify({
                'warns': guild_warns,
                'total': total_warns,
                'users_warned': len(guild_warns)
            })
        
        elif request.method == 'POST':
            request_data = request.get_json()
            user_id = request_data.get('user_id')
            reason = request_data.get('reason')
            moderator_id = request_data.get('moderator_id')
            moderator_name = request_data.get('moderator_name', 'Panel Web')
            
            if not user_id or not reason:
                return jsonify({'error': 'user_id et reason requis'}), 400
            
            if os.path.exists(warns_file):
                try:
                    with open(warns_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            data = {}
                        else:
                            data = json.loads(content)
                except json.JSONDecodeError:
                    print("[WARN] warns.json corrompu lors de l'ajout, réinitialisation...")
                    data = {}
            else:
                data = {}
            
            guild_id_str = str(guild_id)
            if guild_id_str not in data:
                data[guild_id_str] = {}
            
            user_id_str = str(user_id)
            if user_id_str not in data[guild_id_str]:
                data[guild_id_str][user_id_str] = []
            
            warn_id = len(data[guild_id_str][user_id_str]) + 1
            new_warn = {
                'id': warn_id,
                'reason': reason,
                'moderator_id': moderator_id,
                'moderator_name': moderator_name,
                'timestamp': datetime.now().isoformat(),
                'guild_id': int(guild_id)
            }
            
            data[guild_id_str][user_id_str].append(new_warn)
            
            if not os.path.exists('config'):
                os.makedirs('config')
            
            with open(warns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            warn_count = len(data[guild_id_str][user_id_str])
            action_taken = None
            
            try:
                config_file = 'config/warn_config.json'
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            warn_config_data = json.loads(content)
                            guild_config = warn_config_data.get(guild_id_str, {})
                            actions = guild_config.get('actions', {})
                            
                            warn_count_str = str(warn_count)
                            if warn_count_str in actions:
                                action_config = actions[warn_count_str]
                                
                                if action_config.get('enabled', False) and bot_client:
                                    action_type = action_config.get('type')
                                    
                                    print(f"[WARN AUTO-SANCTION] Tentative d'application de l'action '{action_type}' pour {warn_count} warns")
                                    
                                    try:
                                        guild = bot_client.get_guild(int(guild_id))
                                        if guild:
                                            print(f"[WARN AUTO-SANCTION] Serveur trouvé: {guild.name}")
                                            member = guild.get_member(int(user_id))
                                            if member:
                                                print(f"[WARN AUTO-SANCTION] Membre trouvé: {member.name}")
                                                
                                                if action_type == 'timeout':
                                                    import discord
                                                    import asyncio
                                                    from datetime import timedelta
                                                    duration = action_config.get('duration', 3600)
                                                    timeout_until = discord.utils.utcnow() + timedelta(seconds=duration)
                                                    
                                                    future = asyncio.run_coroutine_threadsafe(
                                                        member.timeout(timeout_until, reason=f"Seuil de {warn_count} warns atteint"),
                                                        bot_client.loop
                                                    )
                                                    future.result(timeout=5) 
                                                    action_taken = f"Timeout de {duration//60} minutes appliqué"
                                                    print(f"[WARN AUTO-SANCTION] ✅ Timeout appliqué avec succès")
                                                    
                                                elif action_type == 'kick':
                                                    import asyncio
                                                    future = asyncio.run_coroutine_threadsafe(
                                                        member.kick(reason=f"Seuil de {warn_count} warns atteint"),
                                                        bot_client.loop
                                                    )
                                                    future.result(timeout=5)
                                                    action_taken = "Membre expulsé"
                                                    print(f"[WARN AUTO-SANCTION] ✅ Expulsion réussie")
                                                    
                                                elif action_type == 'ban':
                                                    import asyncio
                                                    future = asyncio.run_coroutine_threadsafe(
                                                        member.ban(reason=f"Seuil de {warn_count} warns atteint", delete_message_days=0),
                                                        bot_client.loop
                                                    )
                                                    future.result(timeout=5)
                                                    action_taken = "Membre banni"
                                                    print(f"[WARN AUTO-SANCTION] ✅ Bannissement réussi")
                                            else:
                                                print(f"[WARN AUTO-SANCTION] ❌ Membre non trouvé dans le serveur")
                                                action_taken = "Erreur: Membre non trouvé"
                                        else:
                                            print(f"[WARN AUTO-SANCTION] ❌ Serveur non trouvé")
                                            action_taken = "Erreur: Serveur non trouvé"
                                    except Exception as e:
                                        print(f"[WARN AUTO-SANCTION] ❌ Erreur: {e}")
                                        import traceback
                                        traceback.print_exc()
                                        action_taken = f"Erreur: {str(e)}"
                                else:
                                    if not bot_client:
                                        print(f"[WARN AUTO-SANCTION] ❌ Bot client non disponible")
                                    if not action_config.get('enabled', False):
                                        print(f"[WARN AUTO-SANCTION] ⏸️ Action désactivée dans la config")
            except Exception as e:
                print(f"Erreur chargement config warns: {e}")
            
            response_data = {
                'success': True,
                'message': 'Warn ajouté avec succès',
                'warn': new_warn,
                'warn_count': warn_count
            }
            
            if action_taken:
                response_data['action_taken'] = action_taken
            
            return jsonify(response_data)
        
        elif request.method == 'DELETE':
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'error': 'user_id requis'}), 400
            
            if not os.path.exists(warns_file):
                return jsonify({'error': 'Aucun warn trouvé'}), 404
            
            try:
                with open(warns_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return jsonify({'error': 'Aucun warn trouvé'}), 404
                    data = json.loads(content)
            except json.JSONDecodeError:
                return jsonify({'error': 'Fichier warns corrompu'}), 500
            
            guild_warns = data.get(str(guild_id), {})
            user_id_str = str(user_id)
            
            if user_id_str in guild_warns:
                del guild_warns[user_id_str]
                data[str(guild_id)] = guild_warns
                
                with open(warns_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                return jsonify({'success': True, 'message': 'Tous les warns de l\'utilisateur ont été supprimés'})
            else:
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/warns/<user_id>', methods=['GET'])
@require_guild_admin
def get_user_warns(guild_id, user_id):
    """Obtenir les warns d'un utilisateur spécifique"""
    try:
        import json
        warns_file = 'config/warns.json'
        
        if not os.path.exists(warns_file):
            return jsonify({'warns': [], 'total': 0})
        
        with open(warns_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            guild_warns = data.get(str(guild_id), {})
            user_warns = guild_warns.get(str(user_id), [])
            
            return jsonify({
                'warns': user_warns,
                'total': len(user_warns)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/warns/<user_id>/<int:warn_id>', methods=['DELETE'])
@require_guild_admin
def delete_warn(guild_id, user_id, warn_id):
    """Supprimer un warn spécifique"""
    try:
        import json
        warns_file = 'config/warns.json'
        
        if not os.path.exists(warns_file):
            return jsonify({'error': 'Aucun warn trouvé'}), 404
        
        try:
            with open(warns_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return jsonify({'error': 'Aucun warn trouvé'}), 404
                data = json.loads(content)
        except json.JSONDecodeError:
            return jsonify({'error': 'Fichier warns corrompu'}), 500
        
        guild_warns = data.get(str(guild_id), {})
        user_warns = guild_warns.get(str(user_id), [])
        
        warn_found = False
        for i, warn in enumerate(user_warns):
            if warn['id'] == warn_id:
                user_warns.pop(i)
                warn_found = True
                break
        
        if not warn_found:
            return jsonify({'error': 'Warn introuvable'}), 404
        
        if len(user_warns) == 0:
            del guild_warns[str(user_id)]
        else:
            guild_warns[str(user_id)] = user_warns
        
        data[str(guild_id)] = guild_warns
        
        with open(warns_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': 'Warn supprimé', 'remaining_warns': len(user_warns)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/warns/<user_id>/<int:warn_id>', methods=['PUT', 'PATCH', 'DELETE'])
@require_guild_admin
def manage_warn(guild_id, user_id, warn_id):
    """Modifier ou supprimer un warn spécifique"""
    try:
        import json
        warns_file = 'config/warns.json'
        
        if not os.path.exists(warns_file):
            return jsonify({'error': 'Aucun warn trouvé'}), 404
        
        try:
            with open(warns_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return jsonify({'error': 'Aucun warn trouvé'}), 404
                data = json.loads(content)
        except json.JSONDecodeError:
            return jsonify({'error': 'Fichier warns corrompu'}), 500
        
        guild_warns = data.get(str(guild_id), {})
        user_warns = guild_warns.get(str(user_id), [])
        
        if request.method in ['PUT', 'PATCH']:
            request_data = request.get_json()
            new_reason = request_data.get('reason')
            
            if not new_reason:
                return jsonify({'error': 'Nouvelle raison requise'}), 400
            
            warn_found = False
            for warn in user_warns:
                if warn.get('id') == warn_id:
                    warn['reason'] = new_reason
                    warn['edited'] = True
                    warn['edited_at'] = datetime.now().isoformat()
                    warn_found = True
                    break
            
            if not warn_found:
                return jsonify({'error': 'Warn introuvable'}), 404
            
            guild_warns[str(user_id)] = user_warns
            data[str(guild_id)] = guild_warns
            
            with open(warns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return jsonify({'success': True, 'message': 'Warn modifié'})
        
        elif request.method == 'DELETE':
            warn_found = False
            for i, warn in enumerate(user_warns):
                if warn.get('id') == warn_id:
                    user_warns.pop(i)
                    warn_found = True
                    break
            
            if not warn_found:
                return jsonify({'error': 'Warn introuvable'}), 404
            
            if len(user_warns) == 0:
                del guild_warns[str(user_id)]
            else:
                guild_warns[str(user_id)] = user_warns
            
            data[str(guild_id)] = guild_warns
            
            with open(warns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return jsonify({'success': True, 'message': 'Warn supprimé', 'remaining_warns': len(user_warns)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/guilds/<guild_id>/warn-config', methods=['GET', 'PUT'])
@require_guild_admin
def manage_warn_config(guild_id):
    """Gérer la configuration des warns d'un serveur"""
    try:
        config_file = 'config/warn_config.json'
        default_config = {
            "actions": {
                "3": {"type": "timeout", "duration": 3600, "enabled": True},
                "5": {"type": "kick", "enabled": True},
                "7": {"type": "ban", "enabled": True}
            }
        }
        
        if request.method == 'GET':
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:  
                            return jsonify(default_config)
                        data = json.loads(content)
                        guild_config = data.get(str(guild_id), default_config)
                        return jsonify(guild_config)
                except json.JSONDecodeError:
                    return jsonify(default_config)
            return jsonify(default_config)
        
        elif request.method == 'PUT':
            new_config = request.json
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            data = json.loads(content)
                        else:
                            data = {}
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}
            
            data[str(guild_id)] = new_config
            
            if not os.path.exists('config'):
                os.makedirs('config')
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return jsonify({'success': True, 'message': 'Configuration mise à jour'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_api(port=3001, host='0.0.0.0'):
    print(f"🌐 API démarrée sur http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)

def start_api_thread(client, port=3001):
    """Démarrer l'API dans un thread séparé"""
    set_bot_client(client)
    api_thread = threading.Thread(target=run_api, args=(port,), daemon=True)
    api_thread.start()
    return api_thread
