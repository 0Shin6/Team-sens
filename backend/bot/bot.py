from http import client
import sqlite3
import discord

conn = sqlite3.connect('../teamsens.db')

@client.tree.command(name="add_news", description="Ajouter une actualité")
async def add_news(interaction: discord.Interaction, titre: str, image: str, desc: str):
    conn = sqlite3.connect('../teamsens.db')
    c = conn.cursor()
    c.execute("INSERT INTO news (titre, image, description) VALUES (?, ?, ?)", (titre, image, desc))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Actualité '{titre}' ajoutée !")