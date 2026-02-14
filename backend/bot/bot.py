import sqlite3
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
conn = sqlite3.connect('../teamsens.db')

@bot.tree.command(name="add_news", description="Ajouter une actualité")
async def add_news(interaction: discord.Interaction, titre: str, image: str, desc: str):
    conn = sqlite3.connect('../teamsens.db')
    c = conn.cursor()
    c.execute("INSERT INTO news (titre, image, description) VALUES (?, ?, ?)", (titre, image, desc))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Actualité '{titre}' ajoutée !")

@bot.tree.command(name="supp_news", description="Retirer une actualité")
async def supp_news(interaction: discord.Interaction, titre:  str):
    conn = sqlite3.connect('../teamsens.db')
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE titre = (?)", (titre))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Actualité '{titre}' retiré !")
