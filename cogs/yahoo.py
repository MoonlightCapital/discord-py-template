from struct import unpack
import nextcord as discord
import json
from nextcord.ext import commands
from yfpy.data import Data
from yfpy.query import YahooFantasySportsQuery as YahooQuery
from yfpy.utils import unpack_data
from yfpy.models import League

class Yahoo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Data.retrieve(filename, yf_query, params=None, data_type_class=None, new_data_dir=None)
    controller = Data('../yahoo', True)

    # api id, secret, league_id
    config = None
    with open('data/private.json') as f:
        config = json.load(f)

    @commands.command()
    async def yahoo_test(self, ctx):
        """
        A test command, which can be used to test components.
        """
        if ctx.guild is not None and (ctx.guild.name != 'Dedotated waam' or ctx.channel.name != 's-p-o-r-t-s'):
            print('Yahoo FF command used outside of sports channel but not in a DM, skipping..\n')
            await ctx.send(':rotating_light: Cannot use a Yahoo FF command in this channel')
            return

        print('Successful Yahoo FF test\n')
        msg = await ctx.send('Successful Yahoo FF test')
        pass

    @commands.command(name='ff-info')
    async def ff_info(self, ctx):
        """
        Retrieve Yahoo Fantasy league scoreboard.
        """
        if ctx.guild is not None and (ctx.guild.name != 'Dedotated waam' or ctx.channel.name != 's-p-o-r-t-s'):
            print('Yahoo FF command used outside of sports channel but not in a DM, skipping..\n')
            await ctx.send(':rotating_light: Cannot use a Yahoo FF command in this channel')
            return
        print('Fetching fantasy league info...\n')

        query = YahooQuery('data/', self.config['league_id'])
        leagueInfo = self.controller.retrieve('league_info', query.get_league_info)
        msg = await ctx.send('League info acquired for: ' + leagueInfo.name)


    @commands.command()
    async def register(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Yahoo(bot))
