import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


        # On ajoute les commandes au groupe
        @bot.tree.command(name="kick", description="Expulse un membre")
        async def kick(interaction: discord.Interaction, member: discord.Member):
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message(
                    "❌ Tu n'as pas la permission d'expulser des membres.",
                    ephemeral=True
                )
                return

            try:
                await member.kick(reason=f"Expulsé par {interaction.user}")
                await interaction.response.send_message(f"{member.mention} a été expulsé ✅")
                print(f"{member} a été expulsé par {interaction.user}")
            except Exception as e:
                await interaction.response.send_message(f"Erreur lors de l'expulsion: {e}")

        @bot.tree.command(name="ban", description="Bannit un membre")
        async def ban(interaction: discord.Interaction, member: discord.Member):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ Tu n'as pas la permission de bannir des membres.",
                    ephemeral=True
                )
                return

            try:
                await member.ban(reason=f"Banni par {interaction.user}")
                await interaction.response.send_message(f"{member.mention} a été banni ✅")
                print(f"{member} a été banni par {interaction.user}")
            except Exception as e:
                await interaction.response.send_message(f"Erreur lors du bannissement: {e}")



async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
