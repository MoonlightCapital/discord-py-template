import nextcord as discord
from nextcord.ext import commands

from internal import confirmation, constants

class Sample(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.bot_has_permissions(add_reactions=True)
    async def test(self, ctx):
        """
        A test command, which can be used to test components.
        """

        msg = await ctx.send('Tested!')

        confirmed = await confirmation.confirm(ctx, msg)

        if confirmed == True:
            await msg.edit(content=f'{constants.CONFIRM_REACTION_EMOJI} Confirmed!')
        elif confirmed == False:
            await msg.edit(content=f'{constants.CANCEL_REACTION_EMOJI} Cancelled!')
        elif confirmed == None:
            await msg.edit(content=f'Timeout!')


def setup(bot):
    bot.add_cog(Sample(bot))
