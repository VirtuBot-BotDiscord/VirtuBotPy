import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Votre bot {bot.user} est ONLINE')
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game("VirtuBot")
    )

@bot.command()
async def hello(ctx):
    await ctx.send("Hello")

BOT = os.getenv("DISCORD_TOKEN")
bot.run(BOT)


