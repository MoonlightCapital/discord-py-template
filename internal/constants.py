"""
This file contains constants that the bot works with.
If you wish to add or edit a constant, please make sure to comment the meaning of the constant and the reason for the edit (if applicable).
"""

VERIFICATION_GUILD_COUNT_TRESHOLD = 75 # The amount of servers required for a bot to be eligible for verification.
BAD_BOT_PERCENTAGE_TRESHOLD = 35 # The % of bot accounts in a server in order for the server to be considered low quality

CONFIRM_REACTION_EMOJI = '🟢' # Reaction emoji used to confirm actions
CANCEL_REACTION_EMOJI = '🟥' # Reaction emoji used to cancel actions

CONFIRMATION_TEXT = f'*Please react to this message with {CONFIRM_REACTION_EMOJI} to continue, or react with {CANCEL_REACTION_EMOJI} to cancel. Waiting for two minutes will cancel the process automatically.*' # Message sent at the bottom of every reaction confirmaation
