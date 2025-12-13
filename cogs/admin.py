import discord
import os
import json
from discord.ext import commands

bot = None

class Admin(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance
        
        # Enregistrer les commandes dans le constructeur
        @bot.tree.command(name="kick", description="Expulse un membre")
        async def kick(interaction: discord.Interaction, membres: discord.Member, raison: str = "Aucune raison fournie"):
            """Expulse un membre du serveur"""
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message(
                    "❌ Tu n'as pas la permission d'expulser des membres.",
                    ephemeral=True
                )
                return

            try:
                await membres.send(f"❌ Vous avez été expulsé du serveur.\n**Modérateur :** {interaction.user}\n**Raison :** {raison}")
            except:
                pass
            
            try:
                await membres.kick(reason=f"Expulsé par {interaction.user} - Raison: {raison}")
                await interaction.response.send_message(f"{membres.mention} a été expulsé ✅")
                print(f"{membres} a été expulsé par {interaction.user}")
            except Exception as e:
                await interaction.response.send_message(f"Erreur lors de l'expulsion: {e}")

        @bot.tree.command(name="ban", description="Bannit un membre")
        async def ban(interaction: discord.Interaction, membres: discord.Member, raison: str = "Aucune raison fournie"):
            """Bannit un membre du serveur"""
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ Tu n'as pas la permission de bannir des membres.",
                    ephemeral=True
                )
                return

            try:
                await membres.send(f"❌ Vous avez été banni du serveur.\n**Modérateur :** {interaction.user}\n**Raison :** {raison}")
            except:
                pass
            
            try:
                await membres.ban(reason=f"Banni par {interaction.user} - Raison: {raison}")
                await interaction.response.send_message(f"{membres.mention} a été banni ✅")
                print(f"{membres} a été banni par {interaction.user}")
            except Exception as e:
                await interaction.response.send_message(f"Erreur lors du bannissement: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
