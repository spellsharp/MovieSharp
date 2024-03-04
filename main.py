from bot import bot
import os
from dotenv import load_dotenv


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
bot.run(discord_token)
