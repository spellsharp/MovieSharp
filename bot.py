import requests
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View
from ui_components import MovieButton, Movie, TVShow, SeriesButton, SettingsView
from dotenv import load_dotenv
import os
import csv

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

load_dotenv()
omdb_token = os.getenv('OMDB_TOKEN')
bot_token = os.getenv('DISCORD_TOKEN')
application_id = os.getenv("APPLICATION_ID")

@bot.tree.command(name="help", description='List of commands')
async def help(interaction: discord.Interaction, private: bool = False):
    if private == 'true':
        private = True
    elif private == 'false':
        private = False
    embed = discord.Embed(title='Help is here!',
                          description='The MovieSharp bot gives you links to any movie or TV show you want to watch for free! Take a look below for usage of commands.',
                          color=discord.Color.blue())
    embed.add_field(name='Movies', value='Use `/movie` along with movie\'s name.', inline=False)
    embed.add_field(name='TV Shows', value='Use `/tvshow` along with the TV show\'s name. Season and Episode are optional arguments.', inline=False)
    embed.add_field(name='Settings', value='Use `/settings` to configure your preferences', inline=False)
    embed.add_field(name='Usage of private as argument', value='While using `/help`, `/movie`, `/tvshow`, set private arguement to True or False based on whether you want to receive responses visible only to you and want to create private threads for TV shows. If you don\'t want to do this every time, you may also use `/settings` to configure your privacy preferences as specified above.', inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=private)


@bot.tree.command(name="movie", description='Search for a movie')
async def movie(interaction: discord.Interaction, *, name: str = None, private: bool = None):
    print(private)
    if private is not None:
        if private == 'true':
            private = True
        elif private == 'false':
            private = False
    else:
        with open('settings.csv', 'r') as file:
                csv_reader = csv.reader(file)
                rows = [row for row in csv_reader]
        for row in rows[1:]:
            if row[0] == str(interaction.user.id):
                private = True if row[2] == 'True' else False
            else:
                private = False

    if not name:
        embed = discord.Embed(title='Error',
                              description='Please provide a TV show name',
                              color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
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
            await interaction.response.send_message(view=view, ephemeral=private)

        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        embed = discord.Embed(title=f'{name}',
                              description='Movie not found',
                              color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


@bot.tree.command(name='tvshow', description='Search for a TV show')
async def tvshow(interaction: discord.Interaction, *, name: str = None, season: int = 1, episode: int = 1, private: bool = None):
    print(private)
    if private is not None:
        if private == 'true' or private == 'True':
            private = True
        elif private == 'false' or private == 'False':
            private = False
        print(private)
    else:
        with open('settings.csv', 'r') as file:
                csv_reader = csv.reader(file)
                rows = [row for row in csv_reader]
        for row in rows[1:]:
            if row[0] == str(interaction.user.id):
                private = True if row[1] == 'True' else False
            else:
                private = False

    if interaction and interaction.channel.type == discord.ChannelType.public_thread:
        embed = discord.Embed(
            title='Error',
            description='This command cannot be used in a thread, please go back to a channel to use it.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not name:
        embed = discord.Embed(
            title='Error',
            description=
            'Please provide a TV show name\nExample: `/tvshow breaking bad`',
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
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
                tvshow = TVShow(series=series, episode=episode, season=season)
                series_button = SeriesButton(tvshow=tvshow, ctx=interaction, bot=bot, private=private)
                view.add_item(series_button)
            await interaction.response.send_message(view=view, ephemeral=private)
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
        embed = discord.Embed(title=f'{name}',
                              description='TV Show not found',
                              color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
@bot.tree.command(name='settings', description='Settings for the bot')
async def settings(interaction: discord.Interaction):
    settingsView = SettingsView(interaction=interaction)
    await interaction.response.send_message(view=settingsView, ephemeral=True)

@bot.tree.command(name='vote', description='Upvote this bot on top.gg')
async def vote(interaction: discord.Interaction):
    embed = discord.Embed(title='Thanks for supporting us! 🎉🎉',
                          description='Please find the link to vote below. \n [Click here to vote](https://top.gg/bot/1213818475794137098/vote)',
                          color=discord.Color.green())
    await interaction.response.send_message(embed=embed)