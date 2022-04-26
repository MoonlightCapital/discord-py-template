import nextcord as discord
from nextcord.ext import commands
import asyncio
from internal import constants

async def clear(ctx: commands.Context, message: discord.Message):
    """
    Creates a confirm/cancel reaction menu that returns True or False depending on which reaction was clicked.

    If a timeout occurs, it will return None.
    """

    def check(r, u):
        return str(r.emoji) in (constants.CLEAR_REACTION_EMOJI) and u.id == ctx.author.id and r.message.id == message.id

    await message.add_reaction(constants.CLEAR_REACTION_EMOJI)

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=120.0, check=check)

        emoji = str(reaction.emoji)

        if emoji == constants.CLEAR_REACTION_EMOJI:
            return True
        else:
            await message.remove_reaction(constants.CLEAR_REACTION_EMOJI, message.author)
            return False
    except asyncio.TimeoutError:
        await message.remove_reaction(constants.CLEAR_REACTION_EMOJI, message.author)
        return False
