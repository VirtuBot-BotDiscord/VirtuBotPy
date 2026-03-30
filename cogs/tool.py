import discord
from discord.ext import commands

class Tool(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        @bot.tree.command(name="say", description="Fait répéter un texte")
        async def say(interaction: discord.Interaction, messages: str):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.",ephemeral=True)
            else:
                print(f"{interaction.user} a utilisé la commande /say et a dis : {messages}")
                await interaction.response.send_message("L'embed a été envoyé avec succès")
                await interaction.channel.send(messages)

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
            
            couleur_choisie = couleurs.get(couleur.lower(), discord.Color.blue())
            
            def is_valid_url(url):
                if not url:
                    return False
                return url.lower().startswith(('http://', 'https://')) and len(url) > 10
            

            embed = discord.Embed(
                title=titre,
                description=description,
                color=couleur_choisie
            )
            

            if auteur:
                embed.set_author(name=auteur)
            
            if image_url and is_valid_url(image_url):
                embed.set_image(url=image_url)
            elif image_url:
                await interaction.response.send_message(f"❌ L'URL de l'image n'est pas valide: {image_url}", ephemeral=True)
                return
            
            if thumbnail_url and is_valid_url(thumbnail_url):
                embed.set_thumbnail(url=thumbnail_url)
            elif thumbnail_url:
                await interaction.response.send_message(f"❌ L'URL de la miniature n'est pas valide: {thumbnail_url}", ephemeral=True)
                return
            
            if footer:
                embed.set_footer(text=footer)
            else:
                embed.set_footer(text=f"Utilisé par {interaction.user}")
            
            print(f"{interaction.user} a utilisé la commande /sayembed avec le titre : {titre}")

            await interaction.response.send_message("L'embed a été envoyé avec succès", ephemeral= True)
            await interaction.channel.send(embed=embed)

        @bot.tree.command(name="partenariats", description="Crée une annonce de partenariat")
        async def partenariats(
            interaction: discord.Interaction,
            nom_serveur: str,
            description: str,
            lien_serveur: str = None
        ):
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"🤝 Nouveau Partenariat : {nom_serveur}",
                description=description,
                color=discord.Color.gold()
            )
            
            if lien_serveur:
                embed.add_field(
                    name="📎 Lien du serveur",
                    value=f"[Rejoindre →]({lien_serveur})",
                    inline=False
                )
            
            embed.set_footer(text=f"Annoncé par {interaction.user}")
            
            print(f"{interaction.user} a créé une annonce de partenariat pour : {nom_serveur}")
            await interaction.response.send_message(embed=embed)

        @bot.tree.command(name="botinfo", description="Affiche les informations du bot")
        async def botinfo(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🤖 Informations sur VirtuBot",
                color=discord.Color.blue()
            )
            embed.add_field(name="Nom du Bot", value=self.bot.user.name, inline=True)
            embed.add_field(name="ID du Bot", value=self.bot.user.id, inline=True)
            embed.add_field(name="Nombre de serveurs", value=len(self.bot.guilds), inline=True)
            embed.add_field(name="Nombre d'utilisateurs", value=len(set(self.bot.get_all_members())), inline=True)
            embed.add_field(name="Préfixe", value="!", inline=True)
            embed.set_footer(text="VirtuBot - Open Source Discord Bot")
            
            await interaction.response.send_message(embed=embed)
            print(f"{interaction.user} a utilisé la commande /botinfo.")

        @bot.tree.command(name="infouser", description="Affiche les informations d'un utilisateur")
        async def infouser(interaction: discord.Interaction, membre: discord.Member):
            embed = discord.Embed(
                title=f"👤 Informations sur {membre}",
                color=discord.Color.green()
            )
            embed.add_field(name="Nom d'utilisateur", value=membre.name, inline=True)
            embed.add_field(name="ID", value=membre.id, inline=True)
            embed.add_field(name="Date de création du compte", value=membre.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
            embed.add_field(name="Date de join au serveur", value=membre.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
            embed.add_field(name="Rôles", value=", ".join([role.mention for role in membre.roles if role.name != "@everyone"]), inline=False)
            embed.set_thumbnail(url=membre.avatar.url if membre.avatar else membre.default_avatar.url)
            embed.set_footer(text="VirtuBot - Open Source Discord Bot")
            
            await interaction.response.send_message(embed=embed)
            print(f"{interaction.user} a utilisé la commande /infouser pour voir les informations de {membre}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tool(bot))
