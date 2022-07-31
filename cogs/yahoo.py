import nextcord as discord
import yfpy
from nextcord.ext import commands

class Yahoo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        """
        A test command, which can be used to test components.
        """
        if ctx.guild is not None and (ctx.guild.name != 'Dedotated waam' or ctx.channel.name != 's-p-o-r-t-s'):
            print('Yahoo FF command used outside of sports channel but not in a DM, skipping..\n')
            await ctx.send(':rotating_light: Cannot use a Yahoo FF command in this channel')
            return

        pass


def setup(bot):
    bot.add_cog(Yahoo(bot))
