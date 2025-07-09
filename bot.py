import discord
import asyncio
import aiohttp

import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env variables
load_dotenv()


# Bot Token & Discord Channel link
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))


# APIs list to hit
API_URLS = [
    # for testing purpose only
    # "https://job-portal-system-backend.vercel.app/",
    # "https://job-portal-system-backend.vercel.app/job_posts/all/",
    # "https://hr-corp-system-drf-backend.vercel.app/employee/list/",

    # alumni connect apis
    "https://alumniconnect.xyz/api/v1/associations/",
    "https://staging.alumniconnect.xyz/api/v1/associations/",
]


intents = discord.Intents.default()
client = discord.Client(intents=intents)

daily_summary = []


async def check_apis():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    
    while True:
        async with aiohttp.ClientSession() as session:
            for url in API_URLS:
                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            msg = f"Error: `{url}` returned status {response.status}"
                            await channel.send(msg)
                            daily_summary.append(f"{datetime.now()}: {msg}")
                except Exception as e:
                    msg = f"Server Down: `{url}` - {e}"
                    await channel.send(msg)
                    daily_summary.append(f"{datetime.now()}: {msg}")
        await asyncio.sleep(300)  # will run each 5 minutes interval


async def daily_report():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while True:
        now = datetime.now()
        if now.hour == 23 and now.minute == 59:
            if daily_summary:
                await channel.send(" **Daily API Summary Report** ")
                for entry in daily_summary[-10:]:
                    await channel.send(entry)
                daily_summary.clear()
        await asyncio.sleep(60)   # It will check only once for one minute


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")




async def main():
    async with client:
        # to run the required tasks
        await asyncio.gather(
            client.start(TOKEN),
            check_apis(),
            daily_report()
        )


# to run the bot
asyncio.run(main())

