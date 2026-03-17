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


def init_database() -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            abreviation TEXT NOT NULL UNIQUE,
            logo TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

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
    c.execute("DELETE FROM news WHERE titre = (?)", (titre,))
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


@bot.tree.command(name="add_team", description="Ajouter une équipe")
async def add_team(
    interaction: discord.Interaction,
    nom: str,
    abreviation: str,
    logo: discord.Attachment,
):
    nom = nom.strip()
    abreviation = abreviation.strip().upper()

    if not nom or not abreviation:
        await interaction.response.send_message(
            "Le nom complet et l'abréviation sont obligatoires.",
            ephemeral=True,
        )
        return

    if logo.content_type is None or not logo.content_type.startswith("image/"):
        await interaction.response.send_message(
            "Le logo doit être une image (png, jpg, webp...).",
            ephemeral=True,
        )
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO teams (nom, abreviation, logo) VALUES (?, ?, ?)",
            (nom, abreviation, logo.url),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        await interaction.response.send_message(
            "Une équipe avec ce nom ou cette abréviation existe déjà.",
            ephemeral=True,
        )
        return
    finally:
        conn.close()

    await interaction.response.send_message(
        f"Equipe '{nom}' ({abreviation}) ajoutée avec succès.",
    )


@bot.tree.command(name="del_team", description="Retirer une équipe")
async def del_team(interaction: discord.Interaction, abreviation: str):
    abreviation = abreviation.strip().upper()

    if not abreviation:
        await interaction.response.send_message(
            "L'abréviation est obligatoire.",
            ephemeral=True,
        )
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM teams WHERE abreviation = ?", (abreviation,))
    conn.commit()
    deleted_rows = c.rowcount
    conn.close()

    if deleted_rows == 0:
        await interaction.response.send_message(
            f"Aucune équipe trouvée pour l'abréviation '{abreviation}'.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(f"Equipe '{abreviation}' retirée.")


@bot.tree.command(name="show_teams", description="Afficher les équipes enregistrées")
async def show_teams(interaction: discord.Interaction):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT nom, abreviation, logo FROM teams ORDER BY nom ASC")
    teams = c.fetchall()
    conn.close()

    if not teams:
        await interaction.response.send_message("Aucune équipe enregistrée.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Equipes enregistrées",
        color=discord.Color.blue(),
    )

    for nom, abreviation, logo in teams:
        embed.add_field(
            name=f"{nom} ({abreviation})",
            value=f"Logo: {logo}",
            inline=False,
        )

    await interaction.response.send_message(embed=embed)


@bot.event
async def on_ready():
    init_database()
    await bot.tree.sync()
    print(f"Bot connecté en tant que {bot.user}")


if __name__ == "__main__":
    token = os.getenv("token_discord")
    if not token:
        raise RuntimeError("token_discord manquant")
    bot.run(token)
