import os
from pathlib import Path
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
db_path = Path(__file__).resolve().parents[1] / "teamsens.db"
conn = sqlite3.connect(db_path)

@bot.tree.command(name="add_news", description="Ajouter une actualité")
async def add_news(interaction: discord.Interaction, titre: str, image: str, desc: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO news (titre, image, description) VALUES (?, ?, ?)", (titre, image, desc))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Actualité '{titre}' ajoutée !")

@bot.tree.command(name="supp_news", description="Retirer une actualité")
async def supp_news(interaction: discord.Interaction, titre:  str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE titre = (?)", (titre))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Actualité '{titre}' retiré !")

@bot.tree.command(name="add_match", description="Ajouter un match")
async def add_match(interaction: discord.Interaction, equipe1: str, equipe2: str, date: str, heure: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO matches (equipe1, equipe2, date, heure) VALUES (?, ?, ?, ?)", (equipe1, equipe2, date, heure))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Match entre '{equipe1}' et '{equipe2}' ajouté !")
    await interaction.response.send_message(f"Identifiant du match : {c.lastrowid} cet identifiant est nécessaire pour modifier ou supprimer le match")

@bot.tree.command(name="edit_match", description="Modifier un match")
async def edit_match(interaction: discord.Interaction, id_match: int, equipe1: str, equipe2: str, date: str, heure: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE matches SET equipe1=?, equipe2=?, date=?, heure=? WHERE id=?", (equipe1, equipe2, date, heure, id_match))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f" Match entre '{equipe1}' et '{equipe2}' modifié !")

@bot.tree.command(name="supp_match", description="Retirer un match")
async def supp_match(interaction: discord.Interaction, id_match: int):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM matches WHERE id = (?)", (id_match,))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"Le match numéro '{id_match}' a été retiré !")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot connecté en tant que {bot.user}")


if __name__ == "__main__":
    token = os.getenv("token_discord")
    if not token:
        raise RuntimeError("token_discord manquant dans les variables d'environnement.")
    bot.run(token)
