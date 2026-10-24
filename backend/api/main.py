from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
import sqlite3
from typing import Any, Optional
import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    from .socials import DEFAULT_SOCIALS, fetch_all_socials, save_stats_to_file
except ImportError:
    from socials import DEFAULT_SOCIALS, fetch_all_socials, save_stats_to_file

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)


def get_db_path() -> Path:
    return Path(os.getenv("DB_PATH", str(Path(__file__).resolve().parents[1] / "teamsens.db")))


def init_database(db_file: Optional[Path] = None) -> None:
    target = db_file or get_db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL;")
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
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_a TEXT NOT NULL,
            team_b TEXT NOT NULL,
            date_heure TEXT NOT NULL,
            jeu TEXT DEFAULT 'Inconnu',
            score TEXT DEFAULT '-'
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            image TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def query_news(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    c = conn.cursor()
    try:
        c.execute("SELECT id, titre, image, description FROM news ORDER BY id DESC LIMIT 5")
        rows = c.fetchall()
        return [
            {
                "id": row[0],
                "titre": row[1],
                "img": row[2],
                "desc": row[3],
            }
            for row in rows
        ]
    except sqlite3.Error:
        return []


def query_matches(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    c = conn.cursor()
    try:
        c.execute("PRAGMA table_info(matches)")
        columns = {row[1] for row in c.fetchall()}

        if {"id", "team_a", "team_b", "date_heure"}.issubset(columns):
            score_col = "m.score" if "score" in columns else "'-'"
            jeu_col = "m.jeu" if "jeu" in columns else "'Inconnu'"
            c.execute(
                f"""
                SELECT
                    m.id,
                    COALESCE(ta.logo, m.team_a) AS team_a,
                    COALESCE(ta.nom, m.team_a) AS team_a_name,
                    COALESCE(tb.logo, m.team_b) AS team_b,
                    COALESCE(tb.nom, m.team_b) AS team_b_name,
                    COALESCE({score_col}, '-') AS score,
                    m.date_heure,
                    COALESCE({jeu_col}, 'Inconnu') AS jeu
                FROM matches m
                LEFT JOIN teams ta ON UPPER(ta.abreviation) = UPPER(m.team_a)
                LEFT JOIN teams tb ON UPPER(tb.abreviation) = UPPER(m.team_b)
                ORDER BY m.id DESC
                LIMIT 5
                """
            )
        elif {"id", "equipe1", "equipe2", "date", "heure"}.issubset(columns):
            c.execute(
                """
                SELECT
                    m.id,
                    COALESCE(ta.logo, m.equipe1) AS team_a,
                    COALESCE(ta.nom, m.equipe1) AS team_a_name,
                    COALESCE(tb.logo, m.equipe2) AS team_b,
                    COALESCE(tb.nom, m.equipe2) AS team_b_name,
                    '-' AS score,
                    (m.date || ' ' || m.heure) AS date_heure,
                    'Inconnu' AS jeu
                FROM matches m
                LEFT JOIN teams ta ON UPPER(ta.abreviation) = UPPER(m.equipe1)
                LEFT JOIN teams tb ON UPPER(tb.abreviation) = UPPER(m.equipe2)
                ORDER BY m.id DESC
                LIMIT 5
                """
            )
        else:
            return []

        rows = c.fetchall()
        return [
            {
                "id": row[0],
                "teamA": row[1],
                "teamAName": row[2],
                "teamB": row[3],
                "teamBName": row[4],
                "score": row[5],
                "date": row[6],
                "jeu": row[7],
            }
            for row in rows
        ]
    except sqlite3.Error:
        return []


async def send_discord_dm(session: aiohttp.ClientSession, token: str, recipient_id: str, content: str) -> None:
    headers = {"Authorization": f"Bot {token}"}
    async with session.post(
        "https://discord.com/api/v10/users/@me/channels",
        headers=headers,
        json={"recipient_id": recipient_id},
        timeout=aiohttp.ClientTimeout(total=10),
    ) as dm_resp:
        if dm_resp.status not in (200, 201):
            body = await dm_resp.text()
            raise RuntimeError(f"Création DM échouée: {dm_resp.status} - {body}")
        dm_json = await dm_resp.json()
        channel_id = dm_json.get("id")
        if not channel_id:
            raise RuntimeError("ID de salon DM manquant")

    async with session.post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        headers=headers,
        json={"content": content},
        timeout=aiohttp.ClientTimeout(total=10),
    ) as msg_resp:
        if msg_resp.status not in (200, 201):
            body = await msg_resp.text()
            raise RuntimeError(f"Envoi DM échoué: {msg_resp.status} - {body}")


socials_cache: dict[str, Any] = dict(DEFAULT_SOCIALS)


async def refresh_socials_loop() -> None:
    global socials_cache
    static_json_path = Path(__file__).resolve().parents[2] / "site" / "public" / "data" / "social_stats.json"
    while True:
        try:
            updated = await fetch_all_socials()
            socials_cache = updated
            save_stats_to_file(updated, static_json_path)
        except Exception:
            pass
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database()
    task = asyncio.create_task(refresh_socials_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="LowSens API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactPayload(BaseModel):
    email: str = ""
    nom: str = ""
    discord: Optional[str] = None
    objet: str = ""
    message: str = ""


@app.get("/api/health")
async def get_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/news")
async def get_news() -> list[dict[str, Any]]:
    db_file = get_db_path()
    if not db_file.exists():
        return []
    conn = sqlite3.connect(db_file)
    try:
        return query_news(conn)
    finally:
        conn.close()


@app.get("/api/matches")
async def get_matches() -> list[dict[str, Any]]:
    db_file = get_db_path()
    if not db_file.exists():
        return []
    conn = sqlite3.connect(db_file)
    try:
        return query_matches(conn)
    finally:
        conn.close()


@app.get("/api/socials")
async def get_socials() -> dict[str, Any]:
    return socials_cache


@app.post("/api/contact")
async def post_contact(payload: ContactPayload) -> JSONResponse:
    token = (os.getenv("token_discord") or "").strip()
    recip_raw = os.getenv("discord_recip") or ""
    recipients = [r.strip() for r in recip_raw.split(",") if r.strip()]

    if not token or not recipients:
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "erreur_recip": [],
                "message": "Discord n'est pas configuré sur le serveur.",
            },
        )

    email = payload.email.strip()
    nom = payload.nom.strip()
    objet = payload.objet.strip()
    message = payload.message.strip()

    if not email or not nom or not objet or not message:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "erreur_recip": [],
                "message": "Champs obligatoires manquants.",
            },
        )

    discord_name = (payload.discord or "").strip() or "Non renseigné"
    contenu = (
        f"Nouveau message via le formulaire de contact\n\n"
        f"Email: {email}\n"
        f"Nom: {nom}\n"
        f"Discord: {discord_name}\n"
        f"Objet: {objet}\n\n"
        f"Message:\n{message}"
    )

    failed: list[str] = []
    async with aiohttp.ClientSession() as session:
        for id_recip in recipients:
            try:
                await send_discord_dm(session, token, id_recip, contenu)
            except Exception as err:
                print(f"Erreur envoi DM à {id_recip}: {err}")
                failed.append(id_recip)

    ok = len(failed) == 0
    status_code = 200 if ok else 502
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": ok,
            "erreur_recip": failed,
            "message": "Message envoyé." if ok else "Message envoyé partiellement.",
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "3000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

