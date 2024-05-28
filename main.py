from bot import bot
import os
from dotenv import load_dotenv


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced commands: {synced} commands")
    except Exception as e:
        print(e)

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
bot.run(discord_token)