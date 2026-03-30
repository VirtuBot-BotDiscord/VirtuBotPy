import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from datetime import datetime

TICKET_CONFIG_FILE = "config/ticket_config.json"
TICKET_DATA_FILE = "config/ticket_data.json"

def load_ticket_config():
    """Charge la configuration des tickets"""
    if os.path.exists(TICKET_CONFIG_FILE):
        with open(TICKET_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_ticket_config(data):
    """Sauvegarde la configuration des tickets"""
    if not os.path.exists('config'):
        os.makedirs('config')
    with open(TICKET_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_guild_config(guild_id):
    """Récupère la config d'un serveur spécifique"""
    config = load_ticket_config()
    guild_id_str = str(guild_id)
    if guild_id_str not in config:
        config[guild_id_str] = {
            'ticket_channel': None,
            'ticket_category': None,
            'archive_category': None,
            'ticket_support_roles': []
        }
        save_ticket_config(config)
    return config[guild_id_str]

def save_guild_config(guild_id, guild_data):
    """Sauvegarde la config d'un serveur spécifique"""
    config = load_ticket_config()
    config[str(guild_id)] = guild_data
    save_ticket_config(config)

def load_ticket_data():
    """Charge les données des tickets (historique, statistiques)"""
    if os.path.exists(TICKET_DATA_FILE):
        with open(TICKET_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_ticket_data(data):
    """Sauvegarde les données des tickets"""
    if not os.path.exists('config'):
        os.makedirs('config')
    with open(TICKET_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_guild_tickets(guild_id):
    """Récupère les tickets d'un serveur spécifique"""
    data = load_ticket_data()
    guild_id_str = str(guild_id)
    if guild_id_str not in data:
        data[guild_id_str] = {
            "tickets": {},
            "user_stats": {}
        }
        save_ticket_data(data)
    return data[guild_id_str]

def save_guild_tickets(guild_id, guild_tickets):
    """Sauvegarde les tickets d'un serveur spécifique"""
    data = load_ticket_data()
    data[str(guild_id)] = guild_tickets
    save_ticket_data(data)

class RoleSelectorView(discord.ui.View):
    def __init__(self, action: str, interaction: discord.Interaction):
        super().__init__(timeout=300)
        self.action = action
        self.original_interaction = interaction
        self.selected_roles = []
        role_select = RoleSelect(action, self.selected_roles, interaction.guild)
        self.add_item(role_select)

        confirm_button = discord.ui.Button(
            label="✅ Confirmer",
            style=discord.ButtonStyle.success,
            disabled=True
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)

        cancel_button = discord.ui.Button(
            label="❌ Annuler",
            style=discord.ButtonStyle.danger
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
    
    async def confirm_callback(self, interaction: discord.Interaction):
        if not self.selected_roles:
            await interaction.response.send_message("❌ Aucun rôle sélectionné.", ephemeral=True)
            return
        await self.process_roles(interaction)
    
    async def cancel_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="❌ Opération annulée",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def process_roles(self, interaction: discord.Interaction):
        guild_config = get_guild_config(interaction.guild.id)
        current_support_roles = guild_config.get('ticket_support_roles', [])
        
        if self.action == "add":
            for role_id in self.selected_roles:
                if role_id not in current_support_roles:
                    current_support_roles.append(role_id)
            action_text = "ajouté(s)"
            color = 0x00ff00
        elif self.action == "remove":
            for role_id in self.selected_roles:
                if role_id in current_support_roles:
                    current_support_roles.remove(role_id)
            action_text = "supprimé(s)"
            color = 0xff9900
        
        guild_config['ticket_support_roles'] = current_support_roles
        save_guild_config(interaction.guild.id, guild_config)
        
        role_names = []
        for role_id in self.selected_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                role_names.append(role.name)
        
        embed = discord.Embed(
            title="✅ Rôles de support mis à jour",
            description=f"Rôles {action_text}: {', '.join(role_names)}",
            color=color
        )
        await interaction.response.edit_message(embed=embed, view=None)

class RoleSelect(discord.ui.Select):
    def __init__(self, action: str, selected_roles: list, guild):
        self.action = action
        self.selected_roles = selected_roles
        
        placeholder_text = {
            "add": "🔍 Sélectionnez les rôles à ajouter...",
            "remove": "🗑️ Sélectionnez les rôles à supprimer..."
        }
        
        options = []
        valid_roles = [
            role for role in guild.roles 
            if not role.is_default() 
            and not role.managed 
            and role.name != "@everyone"
            and not role.permissions.administrator
        ]
        
        for role in valid_roles[:25]:
            options.append(discord.SelectOption(
                label=role.name[:50],
                value=str(role.id),
                emoji="🎭" if role.hoist else "👤",
                description=f"ID: {role.id}"[:100]
            ))
        

        if not options:
            options.append(discord.SelectOption(
                label="Aucun rôle disponible",
                value="none",
                description="Créez des rôles dans votre serveur d'abord"
            ))
        
        super().__init__(
            placeholder=placeholder_text.get(action, "Sélectionnez des rôles..."),
            min_values=1,
            max_values=min(len(options), 10) if options else 1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):

        if "none" in self.values:
            embed = discord.Embed(
                title="❌ Aucun rôle disponible",
                description="Veuillez créer des rôles dans votre serveur avant de configurer les rôles de support.",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        self.selected_roles.clear()
        self.selected_roles.extend([int(value) for value in self.values])
        
        view = self.view
        for item in view.children:
            if isinstance(item, discord.ui.Button) and item.label == "✅ Confirmer":
                item.disabled = False
        
        role_names = []
        for role_id in self.selected_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                role_names.append(role.name)
        
        embed = discord.Embed(
            title=f"🎭 Rôles sélectionnés ({len(self.selected_roles)})",
            description=f"**Rôles choisis:** {', '.join(role_names)}",
            color=0x3498db
        )
        await interaction.response.edit_message(embed=embed, view=view)

class CreateTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Créer un Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            print(f"[tickets] create_ticket button pressed by user={interaction.user.id}")
            await interaction.response.send_modal(TicketModal())
        except Exception as e:
            print(f"[tickets] send_modal failed: {e}")

class TicketModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="🎫 Créer un Ticket")

        self.subject = discord.ui.TextInput(
            label="Sujet du ticket",
            placeholder="Décrivez brièvement votre problème...",
            max_length=100,
            required=True
        )
        self.description = discord.ui.TextInput(
            label="Description détaillée", 
            placeholder="Expliquez votre problème en détail...",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )

        self.add_item(self.subject)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"[tickets] TicketModal.on_submit start - user={interaction.user.id}")
            await interaction.response.defer(ephemeral=True)
        except Exception as e:
            print(f"[tickets] defer failed: {e}")
            try:
                await interaction.response.send_message("✅ Création du ticket en cours...", ephemeral=True)
            except Exception as e2:
                print(f"[tickets] fallback send_message also failed: {e2}")

        try:
            guild_config = get_guild_config(interaction.guild.id)
            guild_tickets = get_guild_tickets(interaction.guild.id)
            
            category_id = guild_config.get('ticket_category')
            category = None
            if category_id:
                category = interaction.guild.get_channel(int(category_id))
            
            if not category:
                try:
                    await interaction.followup.send("❌ Erreur : La catégorie des tickets n'est pas configurée correctement. Contactez un administrateur.", ephemeral=True)
                except:
                    pass
                return

            user = interaction.user
            channel_name = f"ticket-{user.display_name.lower()}"

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }


            for role in interaction.guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)


            support_role_ids = guild_config.get('ticket_support_roles', [])
            for role_id in support_role_ids:
                role = interaction.guild.get_role(role_id)
                if role and not role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)


            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Ticket de {user.display_name} | {self.subject.value}"
            )


            staff_name = f"ticket-{user.display_name.lower()}-staff"
            staff_overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            for role in interaction.guild.roles:
                if role.permissions.administrator:
                    staff_overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            for role_id in support_role_ids:
                r = interaction.guild.get_role(role_id)
                if r:
                    staff_overwrites[r] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            staff_channel = await interaction.guild.create_text_channel(
                name=staff_name,
                category=category,
                overwrites=staff_overwrites,
                topic=f"Staff - ticket de {user.display_name} | {self.subject.value}"
            )


            creator_created_at = None
            try:
                ts = ((int(user.id) >> 22) + 1420070400000) / 1000.0
                creator_created_at = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                creator_created_at = None

            user_id_str = str(user.id)
            guild_id_str = str(interaction.guild.id)
            

            user_ticket_count = 0
            if user_id_str in guild_tickets.get("user_stats", {}):
                user_ticket_count = guild_tickets["user_stats"][user_id_str].get("total_tickets", 0)

            roles_count = len([r for r in user.roles if not r.is_default()])


            embed = discord.Embed(
                title="🎫 Nouveau Ticket",
                description=f"**Sujet:** {self.subject.value}\n\n**Description:**\n{self.description.value}",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.set_author(name=f"{user.display_name} ({user.id})", icon_url=user.display_avatar.url)
            embed.add_field(
                name="Infos créateur", 
                value=f"ID: {user.id}\nCompte créé: {creator_created_at or 'N/A'}\nRôles: {roles_count}\nTickets précédents: {user_ticket_count}", 
                inline=False
            )

            view = TicketControlView()
            await ticket_channel.send(f"👋 {user.mention}", embed=embed, view=view)


            try:
                staff_embed = discord.Embed(
                    title="🔔 Nouveau ticket (staff)", 
                    description=f"Ticket créé par {user.mention} • sujet: **{self.subject.value}**", 
                    color=0x3498db, 
                    timestamp=datetime.now()
                )
                staff_embed.add_field(name="Canal membre", value=ticket_channel.mention, inline=True)
                staff_embed.add_field(name="Canal staff", value=staff_channel.mention, inline=True)
                staff_embed.add_field(
                    name="Infos créateur", 
                    value=f"ID: {user.id}\nTickets précédents: {user_ticket_count}\nRôles: {roles_count}", 
                    inline=False
                )
                await staff_channel.send(embed=staff_embed)
            except Exception as e:
                print(f"Erreur notification staff: {e}")


            ticket_id = str(ticket_channel.id)
            guild_tickets["tickets"][ticket_id] = {
                "user_id": user.id,
                "user_name": user.display_name,
                "guild_id": interaction.guild.id,
                "channel_id": ticket_channel.id,
                "staff_channel_id": staff_channel.id,
                "subject": self.subject.value,
                "description": self.description.value,
                "status": "open",
                "created_at": datetime.now().isoformat(),
                "closed_at": None,
                "priority": "normal",
                "notes": []
            }


            if user_id_str not in guild_tickets["user_stats"]:
                guild_tickets["user_stats"][user_id_str] = {"total_tickets": 0}
            
            guild_tickets["user_stats"][user_id_str]["total_tickets"] += 1

            save_guild_tickets(interaction.guild.id, guild_tickets)
            print(f"✅ Ticket {ticket_id} créé et sauvegardé pour {user.display_name}")

            try:
                await interaction.followup.send(f"✅ Votre ticket a été créé : {ticket_channel.mention}", ephemeral=True)
            except Exception:
                try:
                    await interaction.response.send_message(f"✅ Votre ticket a été créé : {ticket_channel.mention}", ephemeral=True)
                except Exception as e:
                    print(f"Erreur envoi confirmation ticket: {e}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send("❌ Une erreur est survenue lors de la création du ticket.", ephemeral=True)
            except Exception:
                try:
                    await interaction.response.send_message("❌ Une erreur est survenue lors de la création du ticket.", ephemeral=True)
                except Exception:
                    pass

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📋 Claim", style=discord.ButtonStyle.secondary, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        has_permission = (
            interaction.user.guild_permissions.manage_guild or
            interaction.user.guild_permissions.administrator or
            any(role.permissions.manage_guild or role.permissions.administrator for role in interaction.user.roles)
        )
        
        if not has_permission:
            await interaction.response.send_message("❌ Permissions insuffisantes !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Ticket Réclamé",
            description=f"Ce ticket a été pris en charge par {interaction.user.mention}",
            color=0xffa500,
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed)
        

        try:
            guild_tickets = get_guild_tickets(interaction.guild.id)
            ticket_id = str(interaction.channel.id)
            if ticket_id in guild_tickets["tickets"]:
                guild_tickets["tickets"][ticket_id]["notes"].append({
                    "type": "claim",
                    "by": interaction.user.id,
                    "timestamp": datetime.now().isoformat()
                })
                save_guild_tickets(interaction.guild.id, guild_tickets)
        except Exception as e:
            print(f"Erreur sauvegarde claim: {e}")

    @discord.ui.button(label="➕ Rejoindre", style=discord.ButtonStyle.success, custom_id="join_ticket")
    async def join_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.channel.send(f"🟢 **{interaction.user.display_name}** a rejoint le ticket")
            

            try:
                guild_tickets = get_guild_tickets(interaction.guild.id)
                ticket_id = str(interaction.channel.id)
                if ticket_id in guild_tickets["tickets"]:
                    guild_tickets["tickets"][ticket_id]["notes"].append({
                        "type": "join",
                        "user_id": interaction.user.id,
                        "name": str(interaction.user),
                        "timestamp": datetime.now().isoformat()
                    })
                    save_guild_tickets(interaction.guild.id, guild_tickets)
            except Exception as e:
                print(f"Erreur sauvegarde join: {e}")
            
            await interaction.response.send_message("✅ Rejoint enregistré", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("❌ Erreur en annonçant votre arrivée", ephemeral=True)

    @discord.ui.button(label="⚡ Priorité", style=discord.ButtonStyle.primary, custom_id="set_priority")
    async def set_priority_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        class _PrioritySelect(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label='🔵 Low', value='low'),
                    discord.SelectOption(label='🟢 Normal', value='normal'),
                    discord.SelectOption(label='🔶 High', value='high'),
                    discord.SelectOption(label='🔴 Urgent', value='urgent')
                ]
                super().__init__(placeholder='Sélectionnez une priorité...', min_values=1, max_values=1, options=options)

            async def callback(self, select_interaction: discord.Interaction):
                choice = self.values[0]
                try:
                    guild_tickets = get_guild_tickets(select_interaction.guild.id)
                    ticket_id = str(select_interaction.channel.id)
                    
                    if ticket_id in guild_tickets["tickets"]:
                        guild_tickets["tickets"][ticket_id]["priority"] = choice
                        guild_tickets["tickets"][ticket_id]["notes"].append({
                            "type": "priority",
                            "value": choice,
                            "by": select_interaction.user.id,
                            "timestamp": datetime.now().isoformat()
                        })
                        save_guild_tickets(select_interaction.guild.id, guild_tickets)
                    
                    labels = {
                        'low': '🔵 Faible',
                        'normal': '🟢 Normal',
                        'high': '🔶 Élevé',
                        'urgent': '🔴 URGENT'
                    }
                    label = labels.get(choice, choice)
                    await select_interaction.channel.send(f"🔔 Priorité définie sur **{label}** par {select_interaction.user.mention}")
                    await select_interaction.response.edit_message(content=f"Priorité mise à **{label}**", view=None)
                except Exception as e:
                    await select_interaction.response.edit_message(content=f"Erreur lors de la mise à jour: {e}", view=None)

        view = discord.ui.View(timeout=60)
        view.add_item(_PrioritySelect())
        await interaction.response.send_message("Choisissez la priorité:", view=view, ephemeral=True)
    
    @discord.ui.button(label="🔄 Transférer", style=discord.ButtonStyle.secondary, custom_id="transfer_ticket")
    async def transfer_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.permissions.manage_guild or role.permissions.administrator for role in interaction.user.roles):
            await interaction.response.send_message("❌ Permissions insuffisantes !", ephemeral=True)
            return
        await interaction.response.send_modal(TransferModal())
    
    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.secondary, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_permission = (
            interaction.user.guild_permissions.administrator or
            interaction.user.guild_permissions.manage_guild or
            any(role.permissions.administrator for role in interaction.user.roles)
        )
        
        if not has_permission:
            await interaction.response.send_message("❌ Permissions insuffisantes !", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            guild_tickets = get_guild_tickets(interaction.guild.id)
            ticket_id = str(interaction.channel.id)
            
            if ticket_id in guild_tickets["tickets"]:
                ticket_info = guild_tickets["tickets"][ticket_id]
                ticket_info["status"] = "closed"
                ticket_info["closed_at"] = datetime.now().isoformat()
                ticket_info["closed_by"] = interaction.user.id
                
                user_id = ticket_info['user_id']
                user = interaction.guild.get_member(user_id)
                staff_channel_id = ticket_info.get('staff_channel_id')
                staff_channel = interaction.guild.get_channel(staff_channel_id) if staff_channel_id else None

                if user:

                    try:
                        await interaction.channel.set_permissions(user, read_messages=False, send_messages=False)
                    except Exception:
                        pass


                    try:
                        guild_config = get_guild_config(interaction.guild.id)
                        archive_cat_id = guild_config.get('archive_category')
                        if archive_cat_id:
                            archive_cat = interaction.guild.get_channel(archive_cat_id)
                            if archive_cat and isinstance(archive_cat, discord.CategoryChannel):
                                await interaction.channel.edit(category=archive_cat)
                                if staff_channel:
                                    await staff_channel.edit(category=archive_cat)
                    except Exception as e:
                        print(f"Erreur déplacement catégorie archive: {e}")

                    embed = discord.Embed(
                        title="🔒 Ticket Fermé",
                        description=f"L'utilisateur {user.mention} a été retiré du ticket.\nLe ticket a été archivé. Utilisez les boutons ci-dessous pour gérer le ticket.",
                        color=0xff8c00,
                        timestamp=datetime.now()
                    )

                    view = ClosedTicketView()
                    await interaction.followup.send(embed=embed, view=view)
                else:
                    await interaction.followup.send("✅ Ticket fermé, mais utilisateur introuvable !", ephemeral=True)
                
                save_guild_tickets(interaction.guild.id, guild_tickets)
            else:
                await interaction.followup.send("❌ Ticket introuvable !", ephemeral=True)
                
        except Exception as e:
            print(f"Erreur fermeture ticket: {e}")
            try:
                await interaction.followup.send("❌ Erreur lors de la fermeture !", ephemeral=True)
            except:
                pass

class ClosedTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔓 Rouvrir", style=discord.ButtonStyle.success, custom_id="reopen_ticket")
    async def reopen_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        has_permission = (
            interaction.user.guild_permissions.administrator or
            interaction.user.guild_permissions.manage_guild or
            any(role.permissions.administrator for role in interaction.user.roles)
        )
        
        if not has_permission:
            await interaction.response.send_message("❌ Permissions insuffisantes !", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            guild_tickets = get_guild_tickets(interaction.guild.id)
            ticket_id = str(interaction.channel.id)
            
            if ticket_id in guild_tickets["tickets"]:
                ticket_info = guild_tickets["tickets"][ticket_id]
                ticket_info["status"] = "open"
                ticket_info["reopened_at"] = datetime.now().isoformat()
                ticket_info["reopened_by"] = interaction.user.id
                
                user_id = ticket_info['user_id']
                user = interaction.guild.get_member(user_id)
                
                if user:

                    await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
                    

                    try:
                        guild_config = get_guild_config(interaction.guild.id)
                        default_cat_id = guild_config.get('ticket_category')
                        if default_cat_id:
                            default_cat = interaction.guild.get_channel(default_cat_id)
                            if default_cat and isinstance(default_cat, discord.CategoryChannel):
                                await interaction.channel.edit(category=default_cat)
                    except Exception:
                        pass

                    embed = discord.Embed(
                        title="🔓 Ticket Rouvert",
                        description=f"L'utilisateur {user.mention} a été rajouté au ticket.",
                        color=0x00ff00,
                        timestamp=datetime.now()
                    )
                    
                    view = TicketControlView()
                    await interaction.followup.send(f"{user.mention}", embed=embed, view=view)
                else:
                    await interaction.followup.send("✅ Ticket rouvert, mais utilisateur introuvable !", ephemeral=True)
                
                save_guild_tickets(interaction.guild.id, guild_tickets)
            else:
                await interaction.followup.send("❌ Ticket introuvable !", ephemeral=True)
                
        except Exception as e:
            print(f"Erreur réouverture: {e}")
            try:
                await interaction.followup.send("❌ Erreur lors de la réouverture !", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.permissions.administrator for role in interaction.user.roles):
            await interaction.response.send_message("❌ Seuls les administrateurs peuvent supprimer un ticket !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚠️ CONFIRMATION DE SUPPRESSION",
            description="**Voulez-vous vraiment supprimer ce ticket ?**\n\n⚠️ Cette action est **IRRÉVERSIBLE** !",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        view = ConfirmDeleteView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmDeleteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
    
    @discord.ui.button(label="✅ OUI - Supprimer", style=discord.ButtonStyle.danger, custom_id="confirm_delete")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            try:
                guild_tickets = get_guild_tickets(interaction.guild.id)
                ticket_id = str(interaction.channel.id)
                staff_channel = None
                
                if ticket_id in guild_tickets["tickets"]:
                    staff_channel_id = guild_tickets["tickets"][ticket_id].get('staff_channel_id')
                    if staff_channel_id:
                        staff_channel = interaction.guild.get_channel(staff_channel_id)
                    

                    guild_tickets["tickets"][ticket_id]["status"] = "deleted"
                    guild_tickets["tickets"][ticket_id]["deleted_at"] = datetime.now().isoformat()
                    guild_tickets["tickets"][ticket_id]["deleted_by"] = interaction.user.id
                    save_guild_tickets(interaction.guild.id, guild_tickets)
            except Exception as e:
                print(f"Erreur sauvegarde suppression: {e}")
                staff_channel = None

            await interaction.followup.send("✅ Les canaux seront supprimés dans 5 secondes...", ephemeral=True)


            await asyncio.sleep(5)
            try:
                await interaction.channel.delete(reason=f"Ticket supprimé par {interaction.user}")
            except Exception:
                pass
            if staff_channel:
                try:
                    await staff_channel.delete(reason=f"Ticket supprimé (staff) par {interaction.user}")
                except Exception:
                    pass
            
        except Exception as e:
            print(f"Erreur suppression: {e}")
            await interaction.followup.send("❌ Erreur lors de la suppression !", ephemeral=True)
    
    @discord.ui.button(label="❌ NON - Annuler", style=discord.ButtonStyle.secondary, custom_id="cancel_delete")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Suppression Annulée",
            description="Le ticket n'a pas été supprimé.",
            color=0x808080
        )
        await interaction.response.edit_message(embed=embed, view=None)

class TransferModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="🔄 Transférer le Ticket")
        
        self.user_input = discord.ui.TextInput(
            label="Utilisateur à mentionner",
            placeholder="@username ou ID utilisateur",
            max_length=100,
            required=True
        )
        self.reason = discord.ui.TextInput(
            label="Raison du transfert",
            placeholder="Pourquoi transférer ce ticket ?",
            style=discord.TextStyle.paragraph,
            max_length=500,
            required=False
        )
        
        self.add_item(self.user_input)
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        target_text = self.user_input.value.strip()
        resolved = None
        resolved_type = None


        if target_text.startswith('<@&') and target_text.endswith('>'):
            try:
                rid = int(target_text[3:-1])
                role = interaction.guild.get_role(rid)
                if role:
                    resolved = role
                    resolved_type = 'role'
            except:
                pass


        if not resolved and (target_text.startswith('<@') and target_text.endswith('>')):
            try:
                uid = int(target_text.replace('<@', '').replace('!', '').replace('>', '').strip())
                member = interaction.guild.get_member(uid)
                if member:
                    resolved = member
                    resolved_type = 'member'
            except:
                pass


        if not resolved and target_text.isdigit():
            try:
                uid = int(target_text)
                member = interaction.guild.get_member(uid)
                if member:
                    resolved = member
                    resolved_type = 'member'
                else:
                    role = interaction.guild.get_role(uid)
                    if role:
                        resolved = role
                        resolved_type = 'role'
            except:
                pass


        if not resolved:
            member = discord.utils.find(lambda m: m.display_name.lower() == target_text.lower() or m.name.lower() == target_text.lower(), interaction.guild.members)
            if member:
                resolved = member
                resolved_type = 'member'
            else:
                role = discord.utils.get(interaction.guild.roles, name=target_text)
                if role:
                    resolved = role
                    resolved_type = 'role'

        reason_text = self.reason.value or 'Aucune'

        if resolved_type == 'role':
            try:
                await interaction.channel.set_permissions(resolved, read_messages=True, send_messages=True)
            except Exception:
                pass
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔄 Ticket Transféré", 
                    description=f"Le ticket a été transféré au rôle {resolved.mention}\n**Par:** {interaction.user.mention}\n**Raison:** {reason_text}", 
                    color=0x00ffff
                ), 
                ephemeral=False
            )
            try:
                guild_tickets = get_guild_tickets(interaction.guild.id)
                ticket_id = str(interaction.channel.id)
                if ticket_id in guild_tickets["tickets"]:
                    guild_tickets["tickets"][ticket_id]["notes"].append({
                        'type': 'transfer',
                        'by': interaction.user.id,
                        'role_id': resolved.id,
                        'reason': reason_text,
                        'timestamp': datetime.now().isoformat()
                    })
                    save_guild_tickets(interaction.guild.id, guild_tickets)
            except Exception:
                pass

        elif resolved_type == 'member':
            try:
                await interaction.channel.set_permissions(resolved, read_messages=True, send_messages=True)
            except Exception:
                pass
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔄 Ticket Transféré", 
                    description=f"Le ticket a été transféré à {resolved.mention}\n**Par:** {interaction.user.mention}\n**Raison:** {reason_text}", 
                    color=0x00ffff
                ), 
                ephemeral=False
            )
            try:
                guild_tickets = get_guild_tickets(interaction.guild.id)
                ticket_id = str(interaction.channel.id)
                if ticket_id in guild_tickets["tickets"]:
                    guild_tickets["tickets"][ticket_id]["notes"].append({
                        'type': 'transfer',
                        'by': interaction.user.id,
                        'member_id': resolved.id,
                        'reason': reason_text,
                        'timestamp': datetime.now().isoformat()
                    })
                    save_guild_tickets(interaction.guild.id, guild_tickets)
            except Exception:
                pass

        else:
            await interaction.response.send_message("❌ Utilisateur ou rôle introuvable. Veuillez fournir une mention, un ID ou un nom exact.", ephemeral=True)

class TICKETS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(CreateTicketView())
        self.bot.add_view(TicketControlView())
        self.bot.add_view(ClosedTicketView())
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("🎫 TICKETS - Système de tickets chargé (sans base de données)")

    @app_commands.command(name="setup_ticket", description="🎫 Configurer le système de tickets")
    @app_commands.describe(
        channel="Canal où afficher le message de création de tickets",
        category="Catégorie où créer les tickets",
        archive_category="Catégorie pour archiver les tickets fermés (optionnel)"
    )
    async def setup_ticket(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel, 
        category: discord.CategoryChannel,
        archive_category: discord.CategoryChannel = None
    ):
        if not (interaction.user.guild_permissions.administrator or 
                interaction.user.guild_permissions.manage_guild):
            embed = discord.Embed(
                title="❌ Permissions insuffisantes",
                description="Vous devez avoir la permission `Gérer le serveur` ou être administrateur.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_config = get_guild_config(interaction.guild.id)
        
        guild_config['ticket_channel'] = channel.id
        guild_config['ticket_category'] = category.id
        if archive_category:
            guild_config['archive_category'] = archive_category.id
        
        save_guild_config(interaction.guild.id, guild_config)
        
        embed = discord.Embed(
            title="🎫 SYSTÈME DE TICKETS",
            description="Créez un ticket pour obtenir de l'aide de notre équipe de support.",
            color=0x3498db
        )
        embed.add_field(
            name="📋 Comment ça marche ?",
            value="• Cliquez sur **🎫 Créer un Ticket**\n• Remplissez le formulaire\n• Un salon privé sera créé\n• Notre équipe vous aidera !",
            inline=False
        )
        embed.set_footer(text="Support disponible 24/7")
        
        view = CreateTicketView()
        await channel.send(embed=embed, view=view)
        
        confirm_embed = discord.Embed(
            title="✅ Configuration terminée",
            description=f"🎫 **Canal:** {channel.mention}\n📁 **Catégorie:** {category.name}",
            color=0x00ff00
        )
        if archive_category:
            confirm_embed.add_field(name="📦 Archive", value=archive_category.name, inline=False)
        
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

    @app_commands.command(name="ticket_support_roles", description="🎫 Gérer les rôles de support pour les tickets")
    @app_commands.describe(
        action="Ajouter, supprimer ou lister les rôles"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Ajouter", value="add"),
        app_commands.Choice(name="Supprimer", value="remove"),
        app_commands.Choice(name="Lister", value="list")
    ])
    async def ticket_support_roles(self, interaction: discord.Interaction, action: str):
        if not (interaction.user.guild_permissions.administrator or 
                interaction.user.guild_permissions.manage_guild):
            embed = discord.Embed(
                title="❌ Permissions insuffisantes",
                description="Vous devez avoir la permission `Gérer le serveur` ou être administrateur.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_config = get_guild_config(interaction.guild.id)
        current_support_roles = guild_config.get('ticket_support_roles', [])
        
        if action == "list":
            if current_support_roles:
                role_names = []
                for role_id in current_support_roles:
                    role = interaction.guild.get_role(role_id)
                    if role:
                        role_names.append(f"• {role.name} ({role.id})")
                    else:
                        role_names.append(f"• Rôle supprimé ({role_id})")
                
                embed = discord.Embed(
                    title="👥 Rôles de support actuels",
                    description="\n".join(role_names),
                    color=0x3498db
                )
            else:
                embed = discord.Embed(
                    title="👥 Rôles de support",
                    description="Aucun rôle de support configuré.",
                    color=0xffa500
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if action in ["add", "remove"]:
            action_text = {
                "add": "🔍 Ajouter des rôles de support",
                "remove": "🗑️ Supprimer des rôles de support"
            }
            
            embed = discord.Embed(
                title=action_text[action],
                description="Sélectionnez les rôles dans le menu déroulant ci-dessous.",
                color=0x3498db
            )
            
            view = RoleSelectorView(action, interaction)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TICKETS(bot))

