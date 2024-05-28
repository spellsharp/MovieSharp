import requests
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View
from ui_components import MovieButton, Movie, TVShow, SeriesButton
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

load_dotenv()
omdb_token = os.getenv('OMDB_TOKEN')
bot_token = os.getenv('DISCORD_TOKEN')
application_id = os.getenv("APPLICATION_ID")





@bot.tree.command(name="help", description='List of commands')
async def help(interaction: discord.Interaction):
    print("help")
    embed = discord.Embed(title='Help',
                          description='List of commands',
                          color=discord.Color.blue())
    embed.add_field(name='movie', value='`/movie Dune`', inline=False)
    embed.add_field(name='tvshow', value='`/tvshow Seinfeld`', inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="movie", description='Search for a movie')
async def movie(interaction: discord.Interaction, *, name: str = None):
    if not name:
        embed = discord.Embed(title='Error',
                              description='Please provide a TV show name',
                              color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    try:
        response = requests.get(
            f"http://www.omdbapi.com/?apikey={omdb_token}&s={name}&type=movie")
        data = response.json()['Search']
        print(f"/movie {name}")
        try:
            view = View(timeout=None)
            for movie in data:
                movie = Movie(imdb_id=movie['imdbID'], name=movie['Title'])
                movie_button = MovieButton(movie=movie)
                view.add_item(movie_button)
            await interaction.response.send_message(view=view)

        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        embed = discord.Embed(title=f'{name}',
                              description='Movie not found',
                              color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return


@bot.tree.command(name='tvshow', description='Search for a TV show')
async def tvshow(interaction: discord.Interaction, *, name: str = None):
    if not name:
        embed = discord.Embed(
            title='Error',
            description=
            'Please provide a TV show name\nExample: `/tvshow breaking bad`',
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    try:
        response = requests.get(
            f"http://www.omdbapi.com/?apikey={omdb_token}&s={name}&type=series"
        )
        data = response.json()['Search']
        print(f"/tvshow {name}")
        try:
            view = View(timeout=None)
            for series in data:
                tvshow = TVShow(series=series)
                series_button = SeriesButton(tvshow=tvshow, ctx=interaction, bot=bot)
                view.add_item(series_button)
            await interaction.response.send_message(view=view)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
        embed = discord.Embed(title=f'{name}',
                              description='TV Show not found',
                              color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
