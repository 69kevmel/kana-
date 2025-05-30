import os
import datetime
import discord
import feedparser
import asyncio

TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

RSS_FEEDS = [
    'https://www.newsweed.fr/feed/',
    'https://lelabdubonheur.fr/blog/rss',
    'https://www.norml.fr/feed/',
]

intents = discord.Intents.default()
intents.message_content = True

class WeedNewsBot(discord.Client):
    def __init__(self, *, intents):
        super().__init__(intents=intents)
        self.sent_links = set()

    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.fetch_and_send_news())

    async def fetch_and_send_news(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        print(f"✅ Channel trouvé : {channel}")

        while True:
            now = datetime.datetime.utcnow()
            today = now.date()

            print(f"🔄 [{now.strftime('%Y-%m-%d %H:%M:%S')}] Vérification des news en français...")

            all_entries = []

            for feed_url in RSS_FEEDS:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    published = entry.get('published_parsed')
                    if published:
                        entry_date = datetime.date(published.tm_year, published.tm_mon, published.tm_mday)
                        if entry_date == today and entry.link not in self.sent_links:
                            all_entries.append(entry)

            if all_entries:
                # Prendre une news aléatoire non encore postée
                import random
                entry = random.choice(all_entries)
                self.sent_links.add(entry.link)

                message = (
                    f"🌿 **Nouvelles fraîches de la journée sur le cannabis !** 🌿\n"
                    f"**{entry.title}**\n"
                    f"{entry.link}\n\n"
                    f"🗓️ Publié le : {datetime.date(entry.published_parsed.tm_year, entry.published_parsed.tm_mon, entry.published_parsed.tm_mday)}"
                )

                await channel.send(message)
                print(f"✅ News postée : {entry.title}")
            else:
                print("❗ Aucune nouvelle à publier cette fois-ci.")

            print("⏳ Attente de 3 heures avant la prochaine vérification...")
            await asyncio.sleep(3 * 3600)  # 3 heures

    async def on_ready(self):
        print(f"✅ Bot connecté en tant que {self.user}")

client = WeedNewsBot(intents=intents)
client.run(TOKEN)
