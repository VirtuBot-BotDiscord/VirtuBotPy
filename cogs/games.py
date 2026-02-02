import discord
import os
import json
import random
import asyncio
from datetime import timedelta
from discord.ext import commands

bot = None

class Games(commands.Cog):
    def __init__(self, bot_instance: commands.Bot):
        global bot
        bot = bot_instance
        self.bot = bot_instance

        #Commandes de jeux.
        @bot.tree.command(name="jeux-pieces", description="Fait lancer une pièce de monnaie (Pile ou Face)")
        async def jeux_pieces(interaction: discord.Interaction):
            resultat = random.choice(["Pile", "Face"])
            await interaction.response.send_message(f"🪙 Le résultat est : **{resultat}**")
            print(f"{interaction.user} a lancé une pièce et le résultat est {resultat}")

        @bot.tree.command(name="jeux-de", description="Fait lancer un dé à 6 faces")
        async def jeux_de(interaction: discord.Interaction):
            resultat = random.randint(1, 6)
            await interaction.response.send_message(f"🎲 Le résultat est : **{resultat}**")
            print(f"{interaction.user} a lancé un dé et le résultat est {resultat}")

        @bot.tree.command(name="jeux-trouve-nombre", description="Jeu pour deviner un nombre entre 1 et 100")
        async def trouve_nombre(interaction: discord.Interaction, nombre: int):
            if nombre < 1 or nombre > 100:
                await interaction.response.send_message("❌ Veuillez choisir un nombre entre 1 et 100.", ephemeral=True)
                return

            nombre_secret = random.randint(1, 100)
            if nombre == nombre_secret:
                await interaction.response.send_message(f"🎉 Félicitations {interaction.user.mention}! Vous avez deviné le nombre secret **{nombre_secret}**!")
            else:
                await interaction.response.send_message(f"❌ Désolé {interaction.user.mention}, le nombre secret était **{nombre_secret}**. Essayez encore!")
            print(f"{interaction.user} a essayé de deviner le nombre {nombre} et le nombre secret était {nombre_secret}")

        @bot.tree.command(name="jeux-roulette-russe", description="Jeu de roulette russe avec 6 chambres")
        async def roulette_russe(interaction: discord.Interaction):
            chambre = random.randint(1, 6)
            if chambre == 1:
                rd_timeout = random.randint(5,60)
                await interaction.response.send_message(f"💥 Bang! {interaction.user.mention}, vous avez perdu la roulette russe! Tu te prends donc un mute de %s minutes :)"%rd_timeout)
                await interaction.user.timeout(timedelta(minutes=rd_timeout), reason=f"A perdu à la roulette Russe (skill issue)")
            else:
                await interaction.response.send_message(f"😅 Click! {interaction.user.mention}, vous êtes sauf cette fois-ci!")
            print(f"{interaction.user} a joué à la roulette russe et le résultat de la chambre est {chambre}")
        
        @bot.tree.command(name="jeux-de-culture", description="Question de culture générale")
        async def jeux_de_culture(interaction: discord.Interaction):
            questions = {
                "Quelle est la capitale de la France?": "Paris",
                "Combien de continents y a-t-il sur Terre?": "7",
                "Qui a écrit 'Roméo et Juliette'?": "Shakespeare",
                "Quelle est la planète la plus proche du Soleil?": "Mercure",
                "En quelle année l'homme a-t-il marché sur la Lune pour la première fois?": "1969",
                
                "Quelle est la capitale de l'Espagne?": "Madrid",
                "Combien font 9 × 7?": "63",
                "Quel est l'océan le plus grand du monde?": "Pacifique",
                "Qui a peint la Joconde?": "Léonard de Vinci",
                "Quelle est la langue la plus parlée au monde?": "Anglais",
                "Quel est le plus grand désert du monde?": "Sahara",
                "Quelle est la capitale du Japon?": "Tokyo",
                "Quel est le métal le plus léger?": "Lithium",
                "Combien de jours compte une année bissextile?": "366",
                "Quel est l'animal terrestre le plus rapide?": "Guépard",

                "Quel est le plus long fleuve du monde?": "Nil",
                "Quel pays a inventé le papier?": "Chine",
                "Quel est le plus grand mammifère marin?": "Baleine bleue",
                "Quelle est la capitale de l'Italie?": "Rome",
                "Combien de côtés a un hexagone?": "6",
                "Quel est le plus petit pays du monde?": "Vatican",
                "Qui a découvert l'Amérique?": "Christophe Colomb",
                "Quel est l'élément chimique O?": "Oxygène",
                "Quel est le plus grand océan?": "Pacifique",
                "Combien de joueurs dans une équipe de football?": "11",

                "Quelle est la capitale du Canada?": "Ottawa",
                "Quel est l'animal symbole de l'Australie?": "Kangourou",
                "Combien de planètes dans le système solaire?": "8",
                "Qui a écrit 'Le Petit Prince'?": "Antoine de Saint-Exupéry",
                "Quel est le plus grand pays du monde?": "Russie",
                "Quelle est la capitale de l'Allemagne?": "Berlin",
                "Quel est l'organe principal du système nerveux?": "Cerveau",
                "Combien de minutes dans une heure?": "60",
                "Quel est le plus grand continent?": "Asie",
                "Qui a inventé l'ampoule électrique?": "Thomas Edison",

                "Quelle est la capitale du Portugal?": "Lisbonne",
                "Quel est le plus grand océan?": "Pacifique",
                "Combien de dents a un adulte?": "32",
                "Quel est le symbole chimique du fer?": "Fe",
                "Qui a écrit 'Les Misérables'?": "Victor Hugo",
                "Quelle est la capitale de la Chine?": "Pékin",
                "Quel est le plus grand animal terrestre?": "Éléphant d'Afrique",
                "Combien de secondes dans une minute?": "60",
                "Quelle est la capitale de la Russie?": "Moscou",
                "Quel est le plus haut sommet du monde?": "Everest",

                "Quelle est la capitale du Brésil?": "Brasilia",
                "Quel est le plus grand lac d'eau douce?": "Lac Supérieur",
                "Qui a peint 'La Nuit étoilée'?": "Van Gogh",
                "Combien de couleurs dans un arc-en-ciel?": "7",
                "Quel est le plus grand organe du corps humain?": "Peau",
                "Quelle est la capitale de l'Inde?": "New Delhi",
                "Quel est le plus long os du corps humain?": "Fémur",
                "Combien de continents existent?": "7",
                "Qui a créé Mickey Mouse?": "Walt Disney",
                "Quelle est la capitale de l'Égypte?": "Le Caire",

                "Quel est le plus grand volcan du monde?": "Mauna Loa",
                "Quel est le plus petit océan?": "Arctique",
                "Qui a écrit '1984'?": "George Orwell",
                "Quelle est la capitale de la Grèce?": "Athènes",
                "Combien de lettres dans l'alphabet français?": "26",
                "Quel est le plus grand pays d'Afrique?": "Algérie",
                "Quelle est la capitale de l'Australie?": "Canberra",
                "Qui a découvert la pénicilline?": "Alexander Fleming",
                "Quel est le plus grand reptile vivant?": "Crocodile marin",
                "Combien de lunes possède la Terre?": "1",

                "Quelle est la capitale de la Turquie?": "Ankara",
                "Quel est le plus grand océan?": "Pacifique",
                "Qui a écrit 'Harry Potter'?": "J.K. Rowling",
                "Combien de joueurs dans une équipe de basket?": "5",
                "Quel est le plus grand pays d'Amérique du Sud?": "Brésil",
                "Quelle est la capitale de la Suède?": "Stockholm",
                "Quel est le gaz le plus abondant dans l'atmosphère?": "Azote",
                "Combien de jours dans une semaine?": "7",
                "Qui a peint 'Guernica'?": "Pablo Picasso",
                "Quelle est la capitale du Mexique?": "Mexico",

                "Quel est le plus grand désert froid?": "Antarctique",
                "Qui a écrit 'L'Odyssée'?": "Homère",
                "Quelle est la capitale de la Norvège?": "Oslo",
                "Combien de pattes a une araignée?": "8",
                "Quel est le plus grand félin du monde?": "Tigre",
                "Quelle est la capitale du Maroc?": "Rabat",
                "Qui a inventé le téléphone?": "Alexander Graham Bell",
                "Combien de couleurs sur le drapeau français?": "3",
                "Quel est le plus grand océan?": "Pacifique",
                "Quelle est la capitale de l'Argentine?": "Buenos Aires"
                    
                }
            

            question, reponse = random.choice(list(questions.items()))
            await interaction.response.send_message(f"❓ {interaction.user.mention}, voici votre question de culture générale:\n**{question}**\nRépondez dans le salon.", ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                if msg.content.strip().lower() == reponse.lower():
                    await interaction.channel.send(f"🎉 Correct! Bien joué {interaction.user.mention}!")
                else:
                    await interaction.channel.send(f"❌ Incorrect! La bonne réponse était **{reponse}**.")
                print(f"{interaction.user} a répondu à la question '{question}' avec '{msg.content.strip()}' (réponse correcte: '{reponse}')")
            except asyncio.TimeoutError:
                await interaction.channel.send(f"⏰ Temps écoulé! La bonne réponse était **{reponse}**.")
                print(f"{interaction.user} n'a pas répondu à temps à la question '{question}'")

        @bot.tree.command(name="jeux-puissance-4", description="Joue à Puissance 4 contre un joueur invite le")
        async def puissance_4(interaction: discord.Interaction, adversaire: discord.Member):
            if adversaire.bot:
                await interaction.response.send_message("❌ Vous ne pouvez pas jouer contre un bot!", ephemeral=True)
                return
            
            if adversaire.id == interaction.user.id:
                await interaction.response.send_message("❌ Vous ne pouvez pas jouer contre vous-même!", ephemeral=True)
                return

            class AcceptView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                    self.accepted = None
                
                @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.success)
                async def accept_button(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    if btn_interaction.user.id != adversaire.id:
                        await btn_interaction.response.send_message("❌ Seul l'adversaire peut accepter!", ephemeral=True)
                        return
                    
                    self.accepted = True
                    self.stop()
                    await btn_interaction.response.edit_message(content=f"✅ {adversaire.mention} a accepté le défi! La partie commence...", view=None)
                
                @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.danger)
                async def decline_button(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                    if btn_interaction.user.id != adversaire.id:
                        await btn_interaction.response.send_message("❌ Seul l'adversaire peut refuser!", ephemeral=True)
                        return
                    
                    self.accepted = False
                    self.stop()
                    await btn_interaction.response.edit_message(content=f"❌ {adversaire.mention} a refusé le défi.", view=None)
            
            accept_view = AcceptView()
            await interaction.response.send_message(
                f"🔴🟡 {interaction.user.mention} défie {adversaire.mention} à une partie de Puissance 4!\n\n{adversaire.mention}, acceptez-vous le défi?",
                view=accept_view
            )
            
            await accept_view.wait()
            
            if accept_view.accepted is None:
                await interaction.followup.send("⏰ Le défi a expiré (aucune réponse).")
                return
            
            if not accept_view.accepted:
                return

            board = [[0 for _ in range(7)] for _ in range(6)]
            current_player = 1 
            game_over = False
            last_action_time = [discord.utils.utcnow()]
            
            def display_board():
                """Affiche le plateau de jeu"""
                emojis = {0: "⚪", 1: "🔴", 2: "🟡"}
                display = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
                for row in board:
                    display += "".join([emojis[cell] for cell in row]) + "\n"
                return display
            
            def check_winner(player):
                """Vérifie si un joueur a gagné"""

                for row in range(6):
                    for col in range(4):
                        if all(board[row][col+i] == player for i in range(4)):
                            return True
                

                for row in range(3):
                    for col in range(7):
                        if all(board[row+i][col] == player for i in range(4)):
                            return True
                

                for row in range(3, 6):
                    for col in range(4):
                        if all(board[row-i][col+i] == player for i in range(4)):
                            return True
                

                for row in range(3):
                    for col in range(4):
                        if all(board[row+i][col+i] == player for i in range(4)):
                            return True
                
                return False
            
            def is_board_full():
                """Vérifie si le plateau est plein"""
                return all(board[0][col] != 0 for col in range(7))
            
            def drop_piece(column, player):
                """Dépose un jeton dans une colonne"""
                for row in range(5, -1, -1):
                    if board[row][column] == 0:
                        board[row][column] = player
                        return True
                return False
            
            class Puissance4View(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                    self.message = None
                    

                    for i in range(1, 8):
                        button = discord.ui.Button(
                            label=str(i),
                            style=discord.ButtonStyle.primary,
                            custom_id=f"col_{i}"
                        )
                        button.callback = self.create_callback(i-1)
                        self.add_item(button)
                    

                    quit_button = discord.ui.Button(
                        label="❌ Abandonner",
                        style=discord.ButtonStyle.danger,
                        custom_id="quit"
                    )
                    quit_button.callback = self.quit_callback
                    self.add_item(quit_button)
                
                async def on_timeout(self):
                    """Appelé quand le timeout de 5 minutes est atteint"""
                    nonlocal game_over
                    if not game_over:
                        game_over = True
                        embed = discord.Embed(
                            title="⏰ Puissance 4 - Temps écoulé",
                            description=f"{display_board()}\n\n⏰ **La partie a été annulée par inactivité (5 minutes).**",
                            color=0xff0000
                        )
                        if self.message:
                            await self.message.edit(embed=embed, view=None)
                        print(f"Puissance 4: Partie annulée entre {interaction.user} et {adversaire} (inactivité)")
                
                def create_callback(self, col):
                    async def callback(btn_interaction: discord.Interaction):
                        nonlocal current_player, game_over, last_action_time
                        

                        last_action_time[0] = discord.utils.utcnow()
                        

                        expected_player = interaction.user if current_player == 1 else adversaire
                        if btn_interaction.user.id != expected_player.id:
                            await btn_interaction.response.send_message(
                                "❌ Ce n'est pas votre tour!",
                                ephemeral=True
                            )
                            return
                        
                        if game_over:
                            await btn_interaction.response.send_message(
                                "❌ La partie est terminée!",
                                ephemeral=True
                            )
                            return
                        

                        if not drop_piece(col, current_player):
                            await btn_interaction.response.send_message(
                                "❌ Cette colonne est pleine!",
                                ephemeral=True
                            )
                            return
                        

                        if check_winner(current_player):
                            game_over = True
                            winner = interaction.user if current_player == 1 else adversaire
                            embed = discord.Embed(
                                title="🎉 Puissance 4 - Victoire!",
                                description=f"{display_board()}\n\n🏆 **{winner.mention} a gagné!**",
                                color=0x00ff00
                            )
                            await btn_interaction.response.edit_message(embed=embed, view=None)
                            print(f"Puissance 4: {winner} a gagné contre {adversaire if winner == interaction.user else interaction.user}")
                            return
                        

                        if is_board_full():
                            game_over = True
                            embed = discord.Embed(
                                title="🤝 Puissance 4 - Match nul!",
                                description=f"{display_board()}\n\n⚖️ **Match nul! Le plateau est plein.**",
                                color=0xffaa00
                            )
                            await btn_interaction.response.edit_message(embed=embed, view=None)
                            print(f"Puissance 4: Match nul entre {interaction.user} et {adversaire}")
                            return
                        

                        current_player = 2 if current_player == 1 else 1
                        next_player = interaction.user if current_player == 1 else adversaire
                        
                        embed = discord.Embed(
                            title="🔴🟡 Puissance 4",
                            description=f"{display_board()}\n\n**Tour de:** {next_player.mention}\n🔴 {interaction.user.mention} vs 🟡 {adversaire.mention}",
                            color=0x3498db
                        )
                        await btn_interaction.response.edit_message(embed=embed, view=self)
                    
                    return callback
                
                async def quit_callback(self, btn_interaction: discord.Interaction):
                    nonlocal game_over
                    
                    if btn_interaction.user.id not in [interaction.user.id, adversaire.id]:
                        await btn_interaction.response.send_message(
                            "❌ Vous ne faites pas partie de cette partie!",
                            ephemeral=True
                        )
                        return
                    
                    game_over = True
                    winner = adversaire if btn_interaction.user.id == interaction.user.id else interaction.user
                    
                    embed = discord.Embed(
                        title="❌ Puissance 4 - Abandon",
                        description=f"{display_board()}\n\n{btn_interaction.user.mention} a abandonné!\n🏆 **{winner.mention} gagne par forfait!**",
                        color=0xff0000
                    )
                    await btn_interaction.response.edit_message(embed=embed, view=None)
                    print(f"Puissance 4: {btn_interaction.user} a abandonné contre {winner}")
            

            embed = discord.Embed(
                title="🔴🟡 Puissance 4",
                description=f"{display_board()}\n\n**Tour de:** {interaction.user.mention}\n🔴 {interaction.user.mention} vs 🟡 {adversaire.mention}",
                color=0x3498db
            )
            embed.set_footer(text="Cliquez sur un numéro pour jouer dans cette colonne • Partie annulée après 5 min d'inactivité")
            
            view = Puissance4View()
            message = await interaction.followup.send(embed=embed, view=view)
            view.message = message
            print(f"{interaction.user} a défié {adversaire} à une partie de Puissance 4")

        @bot.tree.command(name="jeux-meme", description="Envoie un meme aléatoire")
        async def jeux_meme(interaction: discord.Interaction):
            """Envoie un meme aléatoire depuis le fichier meme.json"""
            try:

                if not os.path.exists('config'):
                    os.makedirs('config')
                

                if not os.path.exists('config/meme.json'):
                    default_memes = {
                        "image1": "votre_lien",
                        "image2": "votre_lien",
                        "image3": "votre_lien"
                    }
                    with open('config/meme.json', 'w', encoding='utf-8') as f:
                        json.dump(default_memes, f, indent=4)
                    print("Fichier config/meme.json créé avec des exemples")
                
                with open('config/meme.json', 'r', encoding='utf-8') as f:
                    memes = json.load(f)
                
                meme_list = list(memes.values())
                if not meme_list:
                    await interaction.response.send_message("❌ Aucun meme disponible!", ephemeral=True)
                    print(f"{interaction.user} a tenté d'obtenir un meme mais la liste est vide")
                    return
                
                random_meme = random.choice(meme_list)
                
                embed = discord.Embed(
                    title="Voici ton meme 😅",
                    color=0x00AE86
                )
                embed.set_image(url=random_meme)
                
                await interaction.response.send_message(embed=embed)
                print(f"{interaction.user} a demandé un meme: {random_meme}")
            except FileNotFoundError:
                await interaction.response.send_message("❌ Le fichier de memes est introuvable!", ephemeral=True)
                print(f"{interaction.user} a tenté d'obtenir un meme mais le fichier est introuvable")
            except Exception as e:
                await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
                print(f"Erreur lors de la commande jeux-meme par {interaction.user}: {e}")



async def setup(bot: commands.Bot):
    await bot.add_cog(Games(bot))
