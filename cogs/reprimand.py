import nextcord as discord
from nextcord.ext import commands

class Reprimand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reprimand(self, ctx, mandee: discord.Member):
        """
        Basic reprimand command, called with the name of the reprimandee.
        """
        response = "" + mandee.display_name + ", you're reprimanded!"

        msg = await ctx.send(response)


def setup(bot):
    bot.add_cog(Reprimand(bot))
