import discord
import os
import json
from discord.ext import commands

bot = None

class Config(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

        # Enregistrer la commande dans le constructeur
        @bot.tree.command(name="adminbot", description="Configuration du serveur")
        async def adminbot(interaction: discord.Interaction):
            """Configuration des vocs temporaires"""
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ Permission manquante.", ephemeral=True)
                return

            config = self._load_config()
            guild_id = str(interaction.guild_id)

            if guild_id not in config:
                config[guild_id] = {
                    "welcome_enabled": False,
                    "leave_enabled": False,
                    "voice_temp_enabled": False,
                    "welcome_channel_id": None,
                    "leave_channel_id": None,
                    "voice_temp_category_id": None,
                    "voice_temp_trigger_channel_id": None,
                    "ticket_enabled": False,
                    "ticket_channel_id": None,
                    "ticket_message": "Cliquez pour créer un ticket"
                }
                self._save_config(config)

            # Menu catégorie
            class VocCategoryView(discord.ui.View):
                def __init__(self, cog):
                    super().__init__(timeout=None)
                    self.cog = cog

                @discord.ui.select(placeholder="Choisir la catégorie", min_values=1, max_values=1, options=[
                    discord.SelectOption(label=cat.name, value=str(cat.id))
                    for cat in interaction.guild.categories[:25]
                ] or [discord.SelectOption(label="Aucune", value="0")])
                async def select_category(self, sel_interaction: discord.Interaction, select: discord.ui.Select):
                    if not sel_interaction.user.guild_permissions.manage_guild:
                        await sel_interaction.response.send_message("❌ Permission manquante.", ephemeral=True)
                        return

                    cat_id = int(select.values[0])
                    if cat_id == 0:
                        await sel_interaction.response.send_message("❌ Aucune catégorie.", ephemeral=True)
                        return

                    cfg = self._load_config()
                    cfg[guild_id]["voice_temp_category_id"] = cat_id
                    self._save_config(cfg)
                    await sel_interaction.response.send_message(f"✅ Catégorie définie.", ephemeral=True)

            # Menu salon de déclenchement
            class VocTriggerView(discord.ui.View):
                def __init__(self, cog):
                    super().__init__(timeout=None)
                    self.cog = cog

                @discord.ui.select(placeholder="Salon de déclenchement", min_values=1, max_values=1, options=[
                    discord.SelectOption(label=ch.name, value=str(ch.id))
                    for ch in interaction.guild.voice_channels[:25]
                ] or [discord.SelectOption(label="Aucun", value="0")])
                async def select_trigger(self, sel_interaction: discord.Interaction, select: discord.ui.Select):
                    if not sel_interaction.user.guild_permissions.manage_guild:
                        await sel_interaction.response.send_message("❌ Permission manquante.", ephemeral=True)
                        return

                    ch_id = int(select.values[0])
                    if ch_id == 0:
                        await sel_interaction.response.send_message("❌ Aucun salon.", ephemeral=True)
                        return

                    cfg = self._load_config()
                    cfg[guild_id]["voice_temp_trigger_channel_id"] = ch_id
                    self._save_config(cfg)
                    await sel_interaction.response.send_message(f"✅ Salon de déclenchement défini.", ephemeral=True)

            # Toggle
            class VocToggleView(discord.ui.View):
                def __init__(self, cog):
                    super().__init__(timeout=None)
                    self.cog = cog

                @discord.ui.button(label="Voc Temp ON/OFF", style=discord.ButtonStyle.success)
                async def toggle(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    if not btn_interaction.user.guild_permissions.manage_guild:
                        await btn_interaction.response.send_message("❌ Permission manquante.", ephemeral=True)
                        return

                    cfg = self._load_config()
                    cfg[guild_id]["voice_temp_enabled"] = not cfg[guild_id].get("voice_temp_enabled", False)
                    self._save_config(cfg)
                    state = "✅ Activé" if cfg[guild_id]["voice_temp_enabled"] else "❌ Désactivé"
                    await btn_interaction.response.send_message(f"Voc temp: {state}.", ephemeral=True)

            cfg = self._load_config()[guild_id]
            embed = discord.Embed(
                title="⚙️ Configuration Voc Temporaire",
                description="Configurer les salons vocaux temporaires",
                color=discord.Color.purple()
            )
            embed.add_field(name="État", value="✅ Activé" if cfg.get("voice_temp_enabled") else "❌ Désactivé", inline=False)
            embed.add_field(name="Catégorie", value=f"<#{cfg.get('voice_temp_category_id')}>" if cfg.get("voice_temp_category_id") else "Non définie", inline=False)
            embed.add_field(name="Salon déclencheur", value=f"<#{cfg.get('voice_temp_trigger_channel_id')}>" if cfg.get("voice_temp_trigger_channel_id") else "Non défini", inline=False)

            await interaction.response.send_message(embed=embed, view=VocToggleView(self), ephemeral=True)

            # Menus séparés
            await interaction.followup.send("Configurez la **catégorie**:", view=VocCategoryView(self), ephemeral=True)
            await interaction.followup.send("Sélectionnez le **salon de déclenchement**:", view=VocTriggerView(self), ephemeral=True)

    def _ensure_file(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def _load_config(self):
        self._ensure_file()
        with open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f) or {}
            except json.JSONDecodeError:
                return {}

    def _save_config(self, config):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)


async def setup(bot_instance: commands.Bot):
    await bot_instance.add_cog(Config(bot_instance))
