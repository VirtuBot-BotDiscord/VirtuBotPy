import discord
import os
import time
import json
from discord.ext import commands

bot = None

class Base(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance
        
        # Enregistrer les commandes dans le constructeur
        @bot.tree.command(name="help", description="Affiche la liste des commandes disponibles.")
        async def help(interaction: discord.Interaction):
            embed = discord.Embed(
                title="VirtuBot",
                description="Liste des commandes VirtuBot.",
                color=discord.Color.green()
            )
            embed.add_field(name="/help", value="Affiche ce message d'aide", inline=True)
            embed.add_field(name="/hello", value="Dis bonjour au bot", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @bot.tree.command(name="hello", description="Dis bonjour au bot")
        async def hello(interaction: discord.Interaction):
            latency_ms = round(self.bot.latency * 1000)
            await interaction.response.send_message(f"Hello 😊 latence: {latency_ms} ms", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Base(bot))