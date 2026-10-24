from __future__ import annotations
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional
import aiohttp


DEFAULT_SOCIALS: dict[str, Any] = {
    "instagram": {
        "count": 49,
        "formatted": "49 abonnés",
        "label": "abonnés",
        "is_live": False,
    },
    "twitch": {
        "count": 196,
        "formatted": "196 followers",
        "label": "followers",
        "is_live": False,
    },
    "youtube": {
        "count": 0,
        "formatted": "Bientôt",
        "label": "abonnés",
        "is_live": False,
    },
    "twitter": {
        "count": 103,
        "formatted": "103 followers",
        "label": "followers",
        "is_live": False,
    },
    "tiktok": {
        "count": 2243,
        "formatted": "2,2 k abonnés",
        "label": "abonnés",
        "is_live": False,
    },
    "discord": {
        "count": 325,
        "formatted": "325 membres",
        "label": "membres",
        "is_live": False,
    },
    "updated_at": str(int(time.time())),
}


def format_followers(count: int, label: str) -> str:
    if count >= 1_000_000:
        val = count / 1_000_000.0
        if round((val % 1) * 10) == 0:
            return f"{int(val)} M {label}"
        return f"{val:.1f}".replace(".", ",") + f" M {label}"
    if count >= 1_000:
        val = count / 1_000.0
        if round((val % 1) * 10) == 0:
            return f"{int(val)} k {label}"
        return f"{val:.1f}".replace(".", ",") + f" k {label}"
    return f"{count} {label}"


async def fetch_discord_count(session: aiohttp.ClientSession, invite_code: str) -> Optional[int]:
    url = f"https://discord.com/api/v10/invites/{invite_code}?with_counts=true"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            if resp.status == 200:
                data = await resp.json()
                count = data.get("approximate_member_count")
                if isinstance(count, int):
                    return count
    except Exception:
        pass
    return None


async def fetch_tiktok_count(session: aiohttp.ClientSession, username: str) -> Optional[int]:
    url = f"https://www.tiktok.com/@{username}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            if resp.status == 200:
                text = await resp.text()
                match = re.search(r'"followerCount":(\d+)', text)
                if match:
                    return int(match.group(1))
    except Exception:
        pass
    return None


async def fetch_twitch_count(session: aiohttp.ClientSession, username: str) -> Optional[int]:
    url = "https://gql.twitch.tv/gql"
    headers = {"Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"}
    payload = {
        "query": f'query {{ user(login: "{username}") {{ followers {{ totalCount }} }} }}'
    }
    try:
        async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
            if resp.status == 200:
                data = await resp.json()
                count = (
                    data.get("data", {})
                    .get("user", {})
                    .get("followers", {})
                    .get("totalCount")
                )
                if isinstance(count, int):
                    return count
    except Exception:
        pass
    return None


async def fetch_all_socials() -> dict[str, Any]:
    stats = json.loads(json.dumps(DEFAULT_SOCIALS))
    stats["updated_at"] = str(int(time.time()))

    discord_invite = os.getenv("DISCORD_INVITE_CODE", "h2aeVVf6T5")
    tiktok_user = os.getenv("TIKTOK_USERNAME", "lowwsens_")
    twitch_user = os.getenv("TWITCH_USERNAME", "lowwsens")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            discord_count = await fetch_discord_count(session, discord_invite)
            if discord_count is not None:
                stats["discord"] = {
                    "count": discord_count,
                    "formatted": format_followers(discord_count, "membres"),
                    "label": "membres",
                    "is_live": True,
                }

            tiktok_count = await fetch_tiktok_count(session, tiktok_user)
            if tiktok_count is not None:
                stats["tiktok"] = {
                    "count": tiktok_count,
                    "formatted": format_followers(tiktok_count, "abonnés"),
                    "label": "abonnés",
                    "is_live": True,
                }

            twitch_count = await fetch_twitch_count(session, twitch_user)
            if twitch_count is not None:
                stats["twitch"] = {
                    "count": twitch_count,
                    "formatted": format_followers(twitch_count, "followers"),
                    "label": "followers",
                    "is_live": True,
                }
    except Exception:
        pass

    return stats


def save_stats_to_file(stats: dict[str, Any], path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

