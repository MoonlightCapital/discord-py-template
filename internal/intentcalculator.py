from discord import Intents

class InvalidFlagException(Exception):
    """An exception thrown when an invalid intent flag is passed"""
    pass

def calculate_intents(raw):
    """
    Calculates the intents from a given input, useful to convert them from a configuration file or a database.

    @param raw: A string/list/tuple/dict representing the intents. Only the special values "all", "none"and "default" can be valid as strings

    @return: An instance of discord.Intents from the raw value passed.
    @raise InvalidFlagException: When a flag string passed is invalid
    """

    intents = Intents()
    intslist = []

    if raw is None or raw == 'none' or 'none' in raw:
        intents = Intents.none()

    if raw == 'default' or 'default' in raw:
        intents = Intents.default()

    if raw == 'all' or 'all' in raw:
        intents = Intents.all()

    if isinstance(raw, str):
        return intents

    if isinstance(raw, dict):
        for k in raw:
            if raw[k]:
                intslist.append(k)

    elif isinstance(raw, list) or isinstance(raw, tuple):
        intslist += raw

    for intent in intslist:
        if intent.lower() in ('all', 'none', 'default'):
            continue

        if intent.lower() not in Intents.VALID_FLAGS:
            raise InvalidFlagException(f'Invalid intent flag passed: {intent}')

        setattr(intents, intent.lower(), True)

    return intents
