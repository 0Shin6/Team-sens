import feedparser
import json
from discord.ext import commands, tasks

idSalonAnnonce = 1367816840843235438
fichier = "suiviReseau.json"

# Liens fixes vers les réseaux
reseaux = {
    "TikTok": "https://www.tiktok.com/@team.sens?_t=8rMrCrODoUT&_r=1",
    "Instagram": "https://www.instagram.com/sensesport_/",
    " Reels": "https://www.instagram.com/sensesport_/reels/",
    "Twitch": "https://m.twitch.tv/team_sens/home?tt_content=channel&tt_medium=mobile_web_share",
    "YouTube": "https://www.youtube.com/@SensEsport",
    "Twitter": "https://x.com/SensTeam_"
}

class GestionnaireReseaux(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.suivi = self.chargerVideo()
        self.verification.start()

    def chargerVideo(self):
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                contenu = f.read().strip()
                if not contenu:
                    self.sauvegardeFichier({})
                    return {}
                return json.loads(contenu)
        except FileNotFoundError:
            self.sauvegardeFichier({})
            return {}
        except json.JSONDecodeError:
            self.sauvegardeFichier({})
            return {}

    def sauvegardeFichier(self, data=None):
        if data is None:
            data = self.suivi
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @tasks.loop(minutes=5)
    async def verification(self):
        salon = self.bot.get_channel(idSalonAnnonce)
        if not salon:
            return None

        
        url =" https://www.youtube.com/@SensEsport"
        flux = feedparser.parse(url)

        if flux.entries:
            derniere_video = flux.entries[0]
            lien = derniere_video.link

            self.sauvegardeFichier()
            await salon.send(f"**La team Sens** vient de sortir une nouvelle vidéo !\n{lien}")

    @verification.before_loop
    async def before_verification(self):
        await self.bot.wait_until_ready()
