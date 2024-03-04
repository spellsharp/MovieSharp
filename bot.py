import requests
import discord
from discord.ext import commands
from discord.ui import View
from ui_components import MovieButton, Movie, TVShow, SeriesButton
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

load_dotenv()
omdb_token = os.getenv('OMDB_TOKEN')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Help', description='List of commands')
    embed.add_field(name='movie', value='`/movie Jurassic Park`', inline=False)
    embed.add_field(name='tvshow', value='`/tvshow The Big Bang Theory`', inline=False)
    await ctx.reply(embed=embed)


@bot.command()
async def movie(ctx, *, name=None):
    if not name:
        embed = discord.Embed(title='Error', description='Please provide a TV show name')
        await ctx.reply(embed=embed)
        return
    try:
        response = requests.get(f"http://www.omdbapi.com/?apikey={omdb_token}&s={name}&type=movie")
        data = response.json()['Search']
        try:
            view = View()
            for movie in data:
                movie = Movie(imdb_id=movie['imdbID'], name=movie['Title'])
                movie_button = MovieButton(movie=movie)
                view.add_item(movie_button)
            await ctx.reply(view=view)

        except Exception as e:
            print(e)
            embed = discord.Embed(title=f'{name}', description='Movie not found')
            await ctx.reply(embed=embed)
            return
    except Exception as e:
        print(e)
        embed = discord.Embed(title=f'{name}', description='Error Processing Request')
        await ctx.reply(embed=embed)
        return
        
@bot.command()
async def tvshow(ctx, *, name=None):
    if not name:
        embed = discord.Embed(title='Error', description='Please provide a TV show name\nExample: /gettv breaking bad')
        await ctx.reply(embed=embed)
        return

    try:
        response = requests.get(f"http://www.omdbapi.com/?apikey={omdb_token}&s={name}&type=series")
        data = response.json()['Search']
        try:
            view =  View()
            for series in data:
                tvshow = TVShow(series=series)
                series_button = SeriesButton(tvshow=tvshow, ctx=ctx, bot=bot)
                view.add_item(series_button)
            await ctx.reply(view=view)
        except Exception as e:
            print(e)

    except:
        embed = discord.Embed(title=f'{name}', description='Error Processing Request')
        await ctx.reply(embed=embed)
        return