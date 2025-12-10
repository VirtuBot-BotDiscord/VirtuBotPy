import discord
import os
import time
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

print("Démarrage du bot...")

#Événement lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f'Votre bot {bot.user} est ONLINE.')
    print('||-- VirtuBot --||')
    time.sleep(2)
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game("VirtuBot")
    )
    for extension in os.listdir('./cogs'):
        if extension.endswith('.py'):
            await bot.load_extension(f'cogs.{extension[:-3]}')
            print(f'Le module cogs.{extension[:-3]} a été chargé.')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} Commandes ont été chargées.")
    except Exception as e:
        print(e)

#Commandes qui regroupent toutes les commandes
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

#Commande simple pour dire bonjour au bot(avec latence)
@bot.tree.command(name="hello", description="Dis bonjour au bot" )
async def hello(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Hello 😊 latence: {latency_ms} ms", ephemeral=True)

BOT = os.getenv("DISCORD_TOKEN")
bot.run(BOT)

