import string
from datetime import datetime
import pytz
import nextcord as discord
from nextcord.ext import commands

class EmoteHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tally-emotes')
    @commands.bot_has_permissions(read_message_history=True)
    async def tally_emotes(self, ctx, channel:discord.TextChannel, after, endRange=None):
        """
        Counts custom emote usage for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)
        """
        emote_dict = {}
        after_date = datetime.strptime(after, '%m-%d-%y')
        before_date = None if endRange is None else pytz.utc.localize(datetime.strptime(after, '%m-%d-%y'))
        for emote in ctx.guild.emojis:
            emote_dict[emote.name] = 0

        async for message in channel.history(before=before_date, after=pytz.utc.localize(after_date)):
            # split message on colons and compare the 2nd - n-1th elements looking for dict entries to increment
            print(str(message.created_at) + ' - ' + message.content)
            splitted = message.content.split(':')
            for section in splitted:
                if section in emote_dict: emote_dict[section] += 1
        
        # sort on descending quantity
        sorted_emotes = dict(sorted(emote_dict.items(), key=lambda x: x[1], reverse=True))
        output = 'Here are the results of the custom emote tally:\n```'
        for k, v in sorted_emotes.items():
            output += k + ' - ' + str(v) + '\n'
        output += '```'

        await ctx.send(output)
    
    @commands.command(name='tally-reactions')
    async def tally_reactions(self, ctx, channel:discord.TextChannel, after, endRange=None):
        """
        Counts custom emote usage as reactions for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)
        """
        emote_dict = {}
        after_date = datetime.strptime(after, '%m-%d-%y')
        before_date = None if endRange is None else pytz.utc.localize(datetime.strptime(after, '%m-%d-%y'))
        for emote in ctx.guild.emojis:
            emote_dict[emote.name] = 0
            

        async for message in channel.history(before=before_date, after=pytz.utc.localize(after_date)):
            # examine reactions
            for reaction in message.reactions:
                if reaction.emoji.name in emote_dict: emote_dict[reaction.emoji.name] += reaction.count
        
        # sort on descending quantity
        sorted_emotes = dict(sorted(emote_dict.items(), key=lambda x: x[1], reverse=True))
        output = 'Here are the results of the custom reaction tally:\n```'
        for k, v in sorted_emotes.items():
            output += k + ' - ' + str(v) + '\n'
        output += '```'

        await ctx.send(output)

def setup(bot):
    bot.add_cog(EmoteHistory(bot))
