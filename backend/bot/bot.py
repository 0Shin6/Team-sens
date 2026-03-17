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


def normalize_abreviation(value: str) -> str:
    return value.strip().upper()


def team_exists(cursor: sqlite3.Cursor, abreviation: str) -> bool:
    cursor.execute("SELECT 1 FROM teams WHERE UPPER(abreviation) = ? LIMIT 1", (abreviation.upper(),))
    return cursor.fetchone() is not None


def get_matches_columns(cursor: sqlite3.Cursor) -> set[str]:
    cursor.execute("PRAGMA table_info(matches)")
    return {row[1] for row in cursor.fetchall()}


def insert_match(cursor: sqlite3.Cursor, equipe1: str, equipe2: str, date: str, heure: str) -> None:
    columns = get_matches_columns(cursor)

    if {"equipe1", "equipe2", "date", "heure"}.issubset(columns):
        cursor.execute(
            "INSERT INTO matches (equipe1, equipe2, date, heure) VALUES (?, ?, ?, ?)",
            (equipe1, equipe2, date, heure),
        )
        return

    if {"team_a", "team_b", "date_heure"}.issubset(columns):
        target_cols = ["team_a", "team_b", "date_heure"]
        values = [equipe1, equipe2, f"{date} {heure}"]

        if "jeu" in columns:
            target_cols.append("jeu")
            values.append("Inconnu")
        if "score" in columns:
            target_cols.append("score")
            values.append("-")

        placeholders = ", ".join(["?"] * len(target_cols))
        cursor.execute(
            f"INSERT INTO matches ({', '.join(target_cols)}) VALUES ({placeholders})",
            tuple(values),
        )
        return

    raise RuntimeError("Schéma de la table matches non reconnu.")


def update_match(cursor: sqlite3.Cursor, id_match: int, equipe1: str, equipe2: str, date: str, heure: str) -> int:
    columns = get_matches_columns(cursor)

    if {"equipe1", "equipe2", "date", "heure"}.issubset(columns):
        cursor.execute(
            "UPDATE matches SET equipe1=?, equipe2=?, date=?, heure=? WHERE id=?",
            (equipe1, equipe2, date, heure, id_match),
        )
        return cursor.rowcount

    if {"team_a", "team_b", "date_heure"}.issubset(columns):
        cursor.execute(
            "UPDATE matches SET team_a=?, team_b=?, date_heure=? WHERE id=?",
            (equipe1, equipe2, f"{date} {heure}", id_match),
        )
        return cursor.rowcount

    raise RuntimeError("Schéma de la table matches non reconnu.")


def fetch_all_matches(cursor: sqlite3.Cursor) -> list[tuple]:
    columns = get_matches_columns(cursor)

    if {"id", "equipe1", "equipe2", "date", "heure"}.issubset(columns):
        cursor.execute("SELECT id, equipe1, equipe2, date, heure, NULL, NULL FROM matches ORDER BY id DESC")
        return cursor.fetchall()

    if {"id", "team_a", "team_b", "date_heure"}.issubset(columns):
        score_expr = "score" if "score" in columns else "NULL"
        jeu_expr = "jeu" if "jeu" in columns else "NULL"
        cursor.execute(
            f"SELECT id, team_a, team_b, date_heure, NULL, {score_expr}, {jeu_expr} FROM matches ORDER BY id DESC"
        )
        return cursor.fetchall()

    raise RuntimeError("Schéma de la table matches non reconnu.")

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
    equipe1 = normalize_abreviation(equipe1)
    equipe2 = normalize_abreviation(equipe2)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if not team_exists(c, equipe1) or not team_exists(c, equipe2):
        conn.close()
        await interaction.response.send_message(
            "Les deux équipes doivent exister dans la base (utilisez leurs abréviations).",
            ephemeral=True,
        )
        return

    try:
        insert_match(c, equipe1, equipe2, date, heure)
    except RuntimeError as err:
        conn.close()
        await interaction.response.send_message(str(err), ephemeral=True)
        return

    match_id = c.lastrowid
    conn.commit()
    conn.close()
    await interaction.response.send_message(
        f"Match entre '{equipe1}' et '{equipe2}' ajouté. ID: {match_id}",
    )

@bot.tree.command(name="edit_match", description="Modifier un match")
async def edit_match(interaction: discord.Interaction, id_match: int, equipe1: str, equipe2: str, date: str, heure: str):
    equipe1 = normalize_abreviation(equipe1)
    equipe2 = normalize_abreviation(equipe2)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if not team_exists(c, equipe1) or not team_exists(c, equipe2):
        conn.close()
        await interaction.response.send_message(
            "Les deux équipes doivent exister dans la base (utilisez leurs abréviations).",
            ephemeral=True,
        )
        return

    try:
        updated_rows = update_match(c, id_match, equipe1, equipe2, date, heure)
    except RuntimeError as err:
        conn.close()
        await interaction.response.send_message(str(err), ephemeral=True)
        return

    conn.commit()
    conn.close()

    if updated_rows == 0:
        await interaction.response.send_message(f"Aucun match trouvé avec l'ID {id_match}.", ephemeral=True)
        return

    await interaction.response.send_message(f" Match entre '{equipe1}' et '{equipe2}' modifié !")

@bot.tree.command(name="del_match", description="Retirer un match")
async def del_match(interaction: discord.Interaction, id_match: int):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM matches WHERE id = (?)", (id_match,))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"Le match numéro '{id_match}' a été retiré !")


@bot.tree.command(name="show_matches", description="Afficher tous les matchs enregistrés")
async def show_matches(interaction: discord.Interaction):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        matches = fetch_all_matches(c)
    except RuntimeError as err:
        conn.close()
        await interaction.response.send_message(str(err), ephemeral=True)
        return

    conn.close()

    if not matches:
        await interaction.response.send_message("Aucun match enregistré.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Matchs enregistrés",
        color=discord.Color.green(),
    )

    for match in matches:
        match_id, equipe1, equipe2, date_value, heure_value, score, jeu = match

        if heure_value:
            date_display = f"{date_value} {heure_value}"
        else:
            date_display = date_value

        details = f"Date: {date_display}"
        if jeu:
            details += f"\nJeu: {jeu}"
        if score:
            details += f"\nScore: {score}"

        embed.add_field(
            name=f"ID {match_id} - {equipe1} vs {equipe2}",
            value=details,
            inline=False,
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="add_team", description="Ajouter une équipe")
async def add_team(
    interaction: discord.Interaction,
    nom: str,
    abreviation: str,
    logo: discord.Attachment,
):
    nom = nom.strip()
    abreviation = normalize_abreviation(abreviation)

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
    abreviation = normalize_abreviation(abreviation)

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
