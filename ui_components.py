import discord
from discord.ui import *
from dotenv import load_dotenv
import os

load_dotenv()
provider_url = os.getenv('PROVIDER_URL')

class MovieButton(Button):
    def __init__(self, movie):
        self.movie = movie
        super().__init__(label=self.movie.name, url=f'{provider_url}?video_id={self.movie.imdb_id}')

class Movie:
    def __init__(self, imdb_id, name):
        self.imdb_id = imdb_id
        self.name = name


class TVShow:
    def __init__(self, series, season=1, episode=1):
        self.imdb_id = series['imdbID']
        self.title = series['Title']
        self.season = season
        self.episode = episode

class NextButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Next Episode')        

    async def callback(self, interaction: discord.Interaction):
        self.tvshow.episode += 1
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'Season {self.tvshow.season} Episode {self.tvshow.episode}', view=self.view, embed=self.embed)

class PreviousButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Previous Episode')

    async def callback(self, interaction: discord.Interaction):
        self.tvshow.episode = max(1, self.tvshow.episode - 1)
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'Season {self.tvshow.season} Episode {self.tvshow.episode}', view=self.view, embed=self.embed)

class NextSeasonButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Next Season')        

    async def callback(self, interaction: discord.Interaction):
        self.tvshow.season += 1
        self.tvshow.episode = 1
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'Season {self.tvshow.season} Episode {self.tvshow.episode}', view=self.view, embed=self.embed)

class PreviousSeasonButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Previous Season')
    
    async def callback(self, interaction: discord.Interaction):
        self.tvshow.season = max(1, self.tvshow.season - 1)
        self.tvshow.episode = 1
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'Season {self.tvshow.season} Episode {self.tvshow.episode}', view=self.view, embed=self.embed)

class SeriesButton(Button):
    def __init__(self, tvshow, ctx, bot):
        self.tvshow = tvshow
        self.ctx = ctx
        self.bot = bot
        super().__init__(label=self.tvshow.title)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        existing_thread = discord.utils.get(self.ctx.guild.threads, name=self.tvshow.title)
        if existing_thread:
            thread = existing_thread
        else:
            thread = await self.ctx.channel.create_thread(name=self.tvshow.title, type=discord.ChannelType.public_thread)
        
        self.embed = discord.Embed(title=f'{self.tvshow.title}', url=f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}')
        self.next_button = NextButton(embed=self.embed, tvshow=self.tvshow)
        self.previous_button = PreviousButton(embed=self.embed, tvshow=self.tvshow)
        self.next_season_button = NextSeasonButton(embed=self.embed, tvshow=self.tvshow)
        self.previous_season_button = PreviousSeasonButton(embed=self.embed, tvshow=self.tvshow)

        await thread.send("> Please provide the season number")
        season_msg = await self.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
        try:
            season = int(season_msg.content)
        except:
            await thread.send("> Please provide a valid season number")
            season_msg = await self.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
            season = int(season_msg.content)


        await thread.send("> Please provide episode number")
        episode_msg = await self.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
        try:
            episode = int(episode_msg.content)
        except:
            await thread.send("> Please provide a valid episode number")
            episode_msg = await self.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
            episode = int(episode_msg.content)


        embed = discord.Embed(title=f"{self.tvshow.title}", url=f'{provider_url}?video_id={self.tvshow.imdb_id}&s={season}&e={episode}')
        view = View()
        view.add_item(self.previous_season_button)
        view.add_item(self.next_season_button)
        view.add_item(self.previous_button)
        view.add_item(self.next_button)
        await thread.send(content=self.tvshow.title, embed=embed, view=view)