import discord
from discord.ext import commands

class Tool(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        #commande pour faire répéter un texte
        @bot.tree.command(name="say", description="Fait répéter un texte")
        async def say(interaction: discord.Interaction, messages: str):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.",ephemeral=True)
            else:
                print(f"{interaction.user} a utilisé la commande /say et a dis : {messages}")
                await interaction.response.send_message(messages)

        @bot.tree.command(name="sayembed", description="Fait répéter un texte sous forme d'embed configurable")
        async def sayembed(
            interaction: discord.Interaction, 
            titre: str,
            description: str,
            couleur: str = "bleu",
            auteur: str = None,
            image_url: str = None,
            thumbnail_url: str = None,
            footer: str = None
        ):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.",ephemeral=True)
                return
            
            # Dictionnaire des couleurs disponibles
            couleurs = {
                "bleu": discord.Color.blue(),
                "rouge": discord.Color.red(),
                "vert": discord.Color.green(),
                "jaune": discord.Color.yellow(),
                "orange": discord.Color.orange(),
                "violet": discord.Color.purple(),
                "rose": discord.Color.magenta(),
                "gris": discord.Color.greyple(),
                "blanc": discord.Color.light_grey(),
                "noir": discord.Color.darker_grey(),
                "gold": discord.Color.gold(),
            }
            
            # Récupère la couleur ou utilise bleu par défaut
            couleur_choisie = couleurs.get(couleur.lower(), discord.Color.blue())
            
            # Crée l'embed
            embed = discord.Embed(
                title=titre,
                description=description,
                color=couleur_choisie
            )
            
            # Ajoute les éléments optionnels
            if auteur:
                embed.set_author(name=auteur)
            
            if image_url:
                embed.set_image(url=image_url)
            
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)
            
            if footer:
                embed.set_footer(text=footer)
            else:
                embed.set_footer(text=f"Utilisé par {interaction.user}")
            
            print(f"{interaction.user} a utilisé la commande /sayembed avec le titre : {titre}")
            await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tool(bot))
