"""
This file contains constants that the bot works with.
If you wish to add or edit a constant, please make sure to comment the meaning of the constant and the reason for the edit (if applicable).
"""

CONFIRM_REACTION_EMOJI = '🟢' # Reaction emoji used to confirm actions
CANCEL_REACTION_EMOJI = '🟥' # Reaction emoji used to cancel actions
CLEAR_REACTION_EMOJI = '❌' # Reaction emoji used to clear a long response
AFFIRMATIVE_REACTION_EMOJI = '👍' # Reaction emoji used to clear a long response

CONFIRMATION_TEXT = f'*Please react to this message with {CONFIRM_REACTION_EMOJI} to continue, or react with {CANCEL_REACTION_EMOJI} to cancel. Waiting for two minutes will cancel the process automatically.*' # Message sent at the bottom of every reaction confirmaation

POSITION_MAP = {
    'QB': 1,
    'RB': 2,
    'WR': 3,
    'TE': 4,
    'D/ST': 16,
    'K': 5,
}

YAHOO_FANTASY_LEAGUE_NAME = 'You Like That!'
