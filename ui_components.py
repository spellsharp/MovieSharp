import csv
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
        super().__init__(label='Next Episode', custom_id='next_button')        

    async def callback(self, interaction: discord.Interaction):
        self.tvshow.episode += 1
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'{self.tvshow.title} S{self.tvshow.season} E{self.tvshow.episode}', view=self.view, embed=self.embed)

class PreviousButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Previous Episode', custom_id='previous_button')

    async def callback(self, interaction: discord.Interaction):
        self.tvshow.episode = max(1, self.tvshow.episode - 1)
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'{self.tvshow.title} S{self.tvshow.season} E{self.tvshow.episode}', view=self.view, embed=self.embed)

class NextSeasonButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Next Season', custom_id='next_season_button')        

    async def callback(self, interaction: discord.Interaction):
        self.tvshow.season += 1
        self.tvshow.episode = 1
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'{self.tvshow.title} S{self.tvshow.season} E{self.tvshow.episode}', view=self.view, embed=self.embed)

class PreviousSeasonButton(Button):
    def __init__(self, embed, tvshow):
        self.embed = embed
        self.tvshow = tvshow
        super().__init__(label='Previous Season', custom_id='previous_season_button')
    
    async def callback(self, interaction: discord.Interaction):
        self.tvshow.season = max(1, self.tvshow.season - 1)
        self.tvshow.episode = 1
        self.embed.url = f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}'
        await interaction.response.edit_message(content=f'{self.tvshow.title} S{self.tvshow.season} E{self.tvshow.episode}', view=self.view, embed=self.embed)

class SeriesButton(Button):
    def __init__(self, tvshow, ctx, bot, private=None):
        self.tvshow = tvshow
        self.ctx = ctx
        self.bot = bot

        if private is not None:
            self.private = private
        else:
            with open('settings.csv', 'r') as file:
                csv_reader = csv.reader(file)
                rows = [row for row in csv_reader]
            for row in rows[1:]:
                if row[0] == str(ctx.user.id):
                    self.private = True if row[1] == 'True' else False
                else:
                    self.private = False
        super().__init__(label=self.tvshow.title)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        existing_thread = discord.utils.get(self.ctx.guild.threads, name=self.tvshow.title)
        if existing_thread and not self.private:
            thread = existing_thread
        else:
            thread = await self.ctx.channel.create_thread(name=self.tvshow.title, type=discord.ChannelType.private_thread if self.private else discord.ChannelType.public_thread)
        
        self.embed = discord.Embed(title=f'{self.tvshow.title}', url=f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}', color=discord.Color.blue())
        self.next_button = NextButton(embed=self.embed, tvshow=self.tvshow)
        self.previous_button = PreviousButton(embed=self.embed, tvshow=self.tvshow)
        self.next_season_button = NextSeasonButton(embed=self.embed, tvshow=self.tvshow)
        self.previous_season_button = PreviousSeasonButton(embed=self.embed, tvshow=self.tvshow)

        embed = discord.Embed(title=f"{self.tvshow.title}", url=f'{provider_url}?video_id={self.tvshow.imdb_id}&s={self.tvshow.season}&e={self.tvshow.episode}', color=discord.Color.blue())
        view = View(timeout=None)
        view.add_item(self.previous_season_button)
        view.add_item(self.next_season_button)  
        view.add_item(self.previous_button)
        view.add_item(self.next_button)
        await thread.send(content=f'{self.tvshow.title} Season {self.tvshow.season} Episode {self.tvshow.episode}', embed=embed, view=view)

class SettingsView(discord.ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.interaction = interaction
        self.movie_select = MovieSelect()
        self.tv_select = TVSelect()
        self.add_item(self.movie_select)
        self.add_item(self.tv_select)

        with open('settings.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            try:
                for row in csv_reader:
                    if row[0] == str(interaction.user.id):
                        self.movie_select.placeholder = 'Set movie response privacy (Currently: True)' if row[2] == 'True' else 'Set movie response privacy (Currently: False)'
                        self.tv_select.placeholder = 'Set TV show response privacy (Currently: True)' if row[1] == 'True' else 'Set TV show response privacy (Currently: False)'
                    else:
                        pass
            except StopIteration:
                pass

class MovieSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='True', value=True),
            discord.SelectOption(label='False', value=False)
        ]
        super().__init__(placeholder='Set movie response privacy', min_values=1, max_values=1, options=options)

    async def callback(self, interaction):
        with open('settings.csv', 'r') as file:
            csv_reader = csv.reader(file)
            rows = [row for row in csv_reader]
        found_user = False
        for row in rows[1:]:
            if row[0] == str(interaction.user.id):
                found_user = True
                row[2] = str(self.values[0])
                break
        if not found_user:
            rows.append([str(interaction.user.id), 'False', str(self.values[0])])

        with open('settings.csv', 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)
        await interaction.response.edit_message(view=SettingsView(interaction))
        

class TVSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='True', value=True),
            discord.SelectOption(label='False', value=False)
        ]
        super().__init__(placeholder='Set TV show response privacy', min_values=1, max_values=1, options=options)

    async def callback(self, interaction):
        with open('settings.csv', 'r') as file:
            csv_reader = csv.reader(file)
            rows = [row for row in csv_reader]
        found_user = False
        for row in rows[1:]:
            if row[0] == str(interaction.user.id):
                found_user = True
                row[1] = str(self.values[0])
                break
        if not found_user:
            rows.append([str(interaction.user.id), str(self.values[0]), 'False'])

        with open('settings.csv', 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)
        await interaction.response.edit_message(view=SettingsView(interaction))
