import discord
from discord.ext import commands

class Panel(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        self.bot = bot_instance

async def setup(bot: commands.Bot):
    await bot.add_cog(Panel(bot))