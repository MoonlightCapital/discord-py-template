import nextcord as discord
from nextcord.ext import commands
import asyncio
from internal import constants

async def author_clear(ctx: commands.Context, message: discord.Message):
    """
    Creates a confirm/cancel reaction menu that returns True or False depending on which reaction was clicked.
    Only accepts reactions that come from the original author of the command.
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

async def clear_on_message_deleted(bot, message: discord.Message, originalMessage: discord.Message):
    """
    Waits to see if another message is deleted to delete the bot's message, or eventually deletes itself unprompted.
    """

    def check(deletedMessage):
        return deletedMessage.id == originalMessage.id

    try:
        await bot.wait_for('message_delete', timeout=300.0, check=check)

        await message.delete()
    except asyncio.TimeoutError:
        await message.delete()
