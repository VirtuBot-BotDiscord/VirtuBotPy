import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from typing import Optional

WARNS_FILE = "config/warns.json"
WARN_CONFIG_FILE = "config/warn_config.json"

DEFAULT_WARN_CONFIG = {
    "actions": {},
    "log_channel": None,
    "dm_enabled": True
}

def load_warns():
    """Charge les warns depuis le fichier JSON"""
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_warn_config():
    """Charge la configuration des warns"""
    if os.path.exists(WARN_CONFIG_FILE):
        with open(WARN_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_warn_config(data):
    """Sauvegarde la configuration des warns"""
    if not os.path.exists('config'):
        os.makedirs('config')
    with open(WARN_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_guild_warn_config(guild_id):
    """Récupère la config warns d'un serveur"""
    config = load_warn_config()
    guild_id_str = str(guild_id)
    if guild_id_str not in config:
        config[guild_id_str] = DEFAULT_WARN_CONFIG.copy()
        config[guild_id_str]["actions"] = {}
        save_warn_config(config)
    return config[guild_id_str]

def save_warns(data):
    """Sauvegarde les warns dans le fichier JSON"""
    if not os.path.exists('config'):
        os.makedirs('config')
    with open(WARNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_guild_warns(guild_id):
    """Récupère les warns d'un serveur"""
    data = load_warns()
    guild_id_str = str(guild_id)
    if guild_id_str not in data:
        data[guild_id_str] = {}
        save_warns(data)
    return data[guild_id_str]

def save_guild_warns(guild_id, guild_warns):
    """Sauvegarde les warns d'un serveur"""
    data = load_warns()
    data[str(guild_id)] = guild_warns
    save_warns(data)

class WARN(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("⚠️ WARN - Système d'avertissements chargé")

    async def log_warn_action(self, guild, embed):
        """Envoie un log dans le salon configuré"""
        config = get_guild_warn_config(guild.id)
        log_channel_id = config.get("log_channel")
        
        if log_channel_id:
            try:
                log_channel = guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Erreur lors de l'envoi du log: {e}")

    @app_commands.command(name="warn", description="⚠️ Avertir un membre")
    @app_commands.describe(
        member="Le membre à avertir",
        reason="Raison de l'avertissement"
    )
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if not (interaction.user.guild_permissions.moderate_members or 
                interaction.user.guild_permissions.administrator):
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Vous devez avoir la permission de modérer les membres.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.guild_permissions.moderate_members or member.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Action impossible",
                description="Vous ne pouvez pas avertir un modérateur ou un administrateur.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_warns = get_guild_warns(interaction.guild.id)
        user_id = str(member.id)
        
        if user_id not in guild_warns:
            guild_warns[user_id] = []
        
        warn_data = {
            "id": len(guild_warns[user_id]) + 1,
            "reason": reason,
            "moderator_id": interaction.user.id,
            "moderator_name": str(interaction.user),
            "timestamp": datetime.now().isoformat(),
            "guild_id": interaction.guild.id
        }
        
        guild_warns[user_id].append(warn_data)
        save_guild_warns(interaction.guild.id, guild_warns)
        
        warn_count = len(guild_warns[user_id])
        
        warn_config = get_guild_warn_config(interaction.guild.id)
        action_taken = None
        action_message = ""
        
        if "actions" in warn_config:
            warn_count_str = str(warn_count)
            if warn_count_str in warn_config["actions"]:
                action_config = warn_config["actions"][warn_count_str]
                
                if action_config.get("enabled", False):
                    action_type = action_config.get("type")
                    
                    try:
                        if action_type == "timeout":
                            duration = action_config.get("duration", 3600)
                            timeout_until = discord.utils.utcnow() + discord.timedelta(seconds=duration)
                            await member.timeout(timeout_until, reason=f"Seuil de {warn_count} warns atteint")
                            action_taken = f"⏰ Timeout de {duration//60} minutes"
                            action_message = f"\n\n**Action automatique:** {action_taken}"
                        
                        elif action_type == "kick":
                            await member.kick(reason=f"Seuil de {warn_count} warns atteint")
                            action_taken = "👢 Expulsion du serveur"
                            action_message = f"\n\n**Action automatique:** {action_taken}"
                        
                        elif action_type == "ban":
                            await member.ban(reason=f"Seuil de {warn_count} warns atteint", delete_message_days=0)
                            action_taken = "🔨 Bannissement du serveur"
                            action_message = f"\n\n**Action automatique:** {action_taken}"
                    
                    except discord.Forbidden:
                        action_message = f"\n\n⚠️ Action automatique échouée (permissions insuffisantes)"
                    except Exception as e:
                        print(f"Erreur action automatique: {e}")
                        action_message = f"\n\n⚠️ Erreur lors de l'action automatique"
        
        warn_config = get_guild_warn_config(interaction.guild.id)
        dm_enabled = warn_config.get("dm_enabled", True)
        
        if dm_enabled:
            try:
                dm_embed = discord.Embed(
                    title="⚠️ Avertissement reçu",
                    description=f"**Serveur:** {interaction.guild.name}\n**Raison:** {reason}",
                    color=0xffa500,
                    timestamp=datetime.now()
                )
                dm_embed.add_field(
                    name="📊 Informations",
                    value=f"**Avertissement:** #{warn_count}\n**Modérateur:** {interaction.user.mention}",
                    inline=False
                )
                if member.avatar:
                    dm_embed.set_thumbnail(url=member.avatar.url)
                dm_embed.set_footer(text=f"Modéré par {interaction.user.name}", icon_url=interaction.user.display_avatar.url if interaction.user.avatar else None)
                await member.send(embed=dm_embed)
            except (discord.Forbidden, discord.HTTPException) as e:
                action_message += "\n\n⚠️ *MP non envoyé (MPs désactivés)*"
        
        embed = discord.Embed(
            title="✅ Avertissement enregistré",
            description=f"**Membre:** {member.mention}\n**Raison:** {reason}",
            color=0xffa500,
            timestamp=datetime.now()
        )
        embed.add_field(name="📊 Avertissements", value=f"Total: **{warn_count}**", inline=True)
        if action_taken:
            embed.add_field(name="⚡ Action automatique", value=action_taken, inline=True)
        embed.set_footer(text=f"Modéré par {interaction.user.name}", icon_url=interaction.user.display_avatar.url if interaction.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)
        
        await self.log_warn_action(interaction.guild, embed)

    @app_commands.command(name="warns", description="📋 Voir les avertissements d'un membre")
    @app_commands.describe(
        member="Le membre à vérifier (optionnel, par défaut vous-même)"
    )
    async def warns(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if member is None:
            member = interaction.user
        
        guild_warns = get_guild_warns(interaction.guild.id)
        user_id = str(member.id)
        
        if user_id not in guild_warns or len(guild_warns[user_id]) == 0:
            embed = discord.Embed(
                title="✅ Aucun avertissement",
                description=f"{member.mention} n'a aucun avertissement enregistré.",
                color=0x10b981
            )
            embed.set_thumbnail(url=member.display_avatar.url if member.avatar else None)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        warns_list = guild_warns[user_id]
        total_warns = len(warns_list)
        
        embed = discord.Embed(
            title=f"⚠️ Avertissements",
            description=f"**Membre:** {member.mention}\n**Total:** {total_warns} avertissement(s)",
            color=0xffa500,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url if member.avatar else None)
        
        for warn in warns_list[-10:]:
            try:
                warn_date = datetime.fromisoformat(warn['timestamp'])
                date_str = warn_date.strftime('%d/%m/%Y à %H:%M')
            except:
                date_str = "Date inconnue"
                
            embed.add_field(
                name=f"#{warn['id']} • {date_str}",
                value=f"**Raison:** {warn['reason']}\n**Modérateur:** {warn['moderator_name']}",
                inline=False
            )
        
        if total_warns > 10:
            embed.set_footer(text=f"Affichage des 10 derniers sur {total_warns} au total")
        else:
            embed.set_footer(text=f"{total_warns} avertissement(s) au total")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unwarn", description="🗑️ Retirer un avertissement spécifique")
    @app_commands.describe(
        member="Le membre concerné",
        warn_id="Numéro de l'avertissement à retirer"
    )
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member, warn_id: int):
        if not (interaction.user.guild_permissions.moderate_members or interaction.user.guild_permissions.administrator):
            embed = discord.Embed(
                title="❌ Permission insuffisante",
                description="Vous devez avoir la permission de **modérer les membres**.",
                color=0xef4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_warns = get_guild_warns(interaction.guild.id)
        user_id = str(member.id)
        
        if user_id not in guild_warns or len(guild_warns[user_id]) == 0:
            embed = discord.Embed(
                title="❌ Aucun avertissement",
                description=f"{member.mention} n'a aucun avertissement à retirer.",
                color=0xef4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        warn_found = None
        for i, warn in enumerate(guild_warns[user_id]):
            if warn['id'] == warn_id:
                warn_found = guild_warns[user_id].pop(i)
                break
        
        if not warn_found:
            embed = discord.Embed(
                title="❌ Avertissement introuvable",
                description=f"L'avertissement **#{warn_id}** n'existe pas pour {member.mention}.",
                color=0xef4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        save_guild_warns(interaction.guild.id, guild_warns)
        
        embed = discord.Embed(
            title="✅ Avertissement retiré",
            description=f"**Membre:** {member.mention}\n**Warn retiré:** #{warn_id}",
            color=0x10b981,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📄 Détails du warn retiré",
            value=f"**Raison:** {warn_found['reason']}\n**Donné par:** {warn_found['moderator_name']}",
            inline=False
        )
        embed.set_footer(text=f"Retiré par {interaction.user.name}", icon_url=interaction.user.display_avatar.url if interaction.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)
        await self.log_warn_action(interaction.guild, embed)


async def setup(bot):
    """Fonction de chargement du cog"""
    await bot.add_cog(WARN(bot))
