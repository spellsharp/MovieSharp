from bot import bot
import os
from dotenv import load_dotenv

try:
    with open('settings.csv', 'r') as file:
        pass
except FileNotFoundError:
    with open('settings.csv', 'w') as file:
        pass

try:
    with open('.env', 'r') as file:
        pass
except FileNotFoundError:
    raise FileNotFoundError("Please create a .env file with the DISCORD_TOKEN and other variables.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced command(s): {len(synced)}")
    except Exception as e:
        print(e)

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
bot.run(discord_token)