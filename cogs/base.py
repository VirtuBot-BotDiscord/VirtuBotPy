import discord
from discord.ext import commands

bot = None

class Base(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance
        
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
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:
            try:
                from api import main as api_module
                
                params = {}
                if hasattr(interaction, 'namespace'):
                    for key, value in interaction.namespace.__dict__.items():
                        if not key.startswith('_'):
                            params[key] = str(value) if value is not None else None
                
                api_module.log_command(
                    interaction.command.name,
                    f"{interaction.user.name}#{interaction.user.discriminator}",
                    interaction.guild.name if interaction.guild else "DM",
                    interaction.guild.id if interaction.guild else None,
                    params,
                    interaction.channel.name if hasattr(interaction.channel, 'name') else "DM"
                )
            except Exception as e:
                print(f"Erreur lors du log de commande: {e}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log les erreurs de commandes"""
        try:
            from api import main as api_module
            
            error_code = "ERR_UNKNOWN"
            error_msg = str(error)
            
            if isinstance(error, commands.MissingPermissions):
                error_code = "ERR_PERMS"
                error_msg = "Permissions insuffisantes"
            elif isinstance(error, commands.MissingRequiredArgument):
                error_code = "ERR_ARGS"
                error_msg = f"Argument manquant: {error.param.name}"
            elif isinstance(error, commands.CommandNotFound):
                error_code = "ERR_CMD_NOT_FOUND"
                error_msg = "Commande introuvable"
            elif isinstance(error, commands.CommandOnCooldown):
                error_code = "ERR_COOLDOWN"
                error_msg = f"Cooldown: {error.retry_after:.2f}s"
            
            api_module.log_error(
                error_code,
                error_msg,
                f"{ctx.author.name}#{ctx.author.discriminator}" if ctx.author else "Unknown",
                ctx.guild.name if ctx.guild else "DM",
                ctx.command.name if ctx.command else None,
                {'full_error': str(error)}
            )
        except Exception as e:
            print(f"Erreur lors du log d'erreur: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Base(bot))