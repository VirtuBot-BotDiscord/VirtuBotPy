import discord
import os
import json
import random
from discord.ext import commands

bot = None

class Games(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance


        @bot.tree.command(name="jeux-pieces", description="Fait lancer une pièce de monnaie (Pile ou Face)")
        async def jeux_pieces(interaction: discord.Interaction):
            resultat = random.choice(["Pile", "Face"])
            await interaction.response.send_message(f"🪙 Le résultat est : **{resultat}**")
            print(f"{interaction.user} a lancé une pièce et le résultat est {resultat}")




async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
