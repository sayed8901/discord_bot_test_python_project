import discord
import asyncio
import aiohttp

import os
import json

from datetime import datetime
from dotenv import load_dotenv


# Load .env variables
load_dotenv()


# Bot Token & Discord Channel ID
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))




# Load API URLs from JSON file
API_FILE = "api_urls.json"



def load_api_urls():
    try:
        with open(API_FILE, "r") as file:
            data = json.load(file)
            return data.get("urls", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_api_urls(urls):
    with open(API_FILE, "w") as file:
        json.dump({"urls": urls}, file, indent=4)


API_URLS = load_api_urls()




# Discord Intents Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  

client = discord.Client(intents=intents)



# Logs
daily_summary_logs = []
ping_count = 0




# ------------------- API CHECK TASK -------------------
async def check_apis():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    global ping_count               # to count the number of pings


    while True:
        async with aiohttp.ClientSession() as session:
            for url in API_URLS:
                ping_count += 1     # increase the number of pings

                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            msg = f"❗ Error: `{url}` returned status {response.status}"
                            await channel.send(msg)
                            daily_summary_logs.append(f"{datetime.now()}: {msg}")
                except Exception as e:
                    msg = f"🚫 Server Down: `{url}` - {e}"
                    await channel.send(msg)
                    daily_summary_logs.append(f"{datetime.now()}: {msg}")

        await asyncio.sleep(600)  # will run in every 10 minutes interval





# ------------------- DAILY REPORT TASK -------------------
async def daily_report():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    global ping_count               # to count the number of pings


    while True:
        now = datetime.now()

        if now.hour == 20 and now.minute == 00:   # at 8:00 PM every night
            await channel.send("📊 **Daily API Summary Report**")

            if daily_summary_logs:
                await channel.send("🚨 Errors detected today:")

                for entry in daily_summary_logs[-10:]:
                    await channel.send(entry)

            else:
                await channel.send("✅ No errors detected. All APIs were up and running smoothly.")

            await channel.send(f"🔄 Total API checks performed today: `{ping_count}`")


            # Clear logs and reset counter
            daily_summary_logs.clear()
            ping_count = 0


        await asyncio.sleep(60)  # It will check only once for one minute





# ------------------- HANDLE DISCORD COMMANDS -------------------
@client.event
async def on_message(message):
    if message.author == client.user:
        return


    content = message.content.strip()
    

    # Add API
    if content.startswith("/add_api "):
        parts = content.split(" ", 1)
        url = parts[1].strip()

        if url in API_URLS:
            await message.channel.send("⚠️ This API is already being monitored.")
        else:
            API_URLS.append(url)
            save_api_urls(API_URLS)
            await message.channel.send(f"✅ Added `{url}` to monitoring list.")



    # Remove API
    elif content.startswith("/remove_api "):
        parts = content.split(" ", 1)
        url = parts[1].strip()

        if url in API_URLS:
            API_URLS.remove(url)
            save_api_urls(API_URLS)
            await message.channel.send(f"✅ Removed `{url}` from monitoring list.")
        else:
            await message.channel.send("⚠️ This API is not in the monitoring list.")



    # List APIs
    elif content.startswith("/list_apis"):
        if API_URLS:
            api_list = "\n".join(f"🔹 {url}" for url in API_URLS)
            await message.channel.send(f"**Currently Monitored APIs:**\n{api_list}")
        else:
            await message.channel.send("🚫 No APIs are currently being monitored.")




# ------------------- BOT READY EVENT -------------------
@client.event
async def on_ready():
    print(f"✅ Bot logged in as {client.user}")





# ------------------- START BOT -------------------
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