# Waambot: A Discord bot for denizens of the Dedotated waam Discord Server

This bot was spawned from a template written in Python to develop a Discord bot and deploy via Docker container. 

The template is available at https://github.com/MoonlightCapital/discord-py-template

## Modules (Cogs):

### archive

These commands are capable of recording an entire Discord text channel locally on the machine that is running the bot. I assigned it to a volume in `docker-compose.yml` to store the archives, so that a new prospective bot owner can easily set that location.

#### wb archive

Owner only. Records text log history of this channel onto the bot's storage. Attachments are skipped, but links remain. 

#### wb archive all

Owner only. Records entire history of this channel onto the bot's storage. All images are downloaded and the text log is saved.

### autoreply

Facilitate setting an out-of-office sort of message. The bot will automatically reply to users who tag somebody with an autoreply message set. The bot owner is also able to visualize and/or clear existing autoreplies for a user if they need to be blown away.

#### wb autoreply

Sets up or modifies an autoreply message for the command author. If no message is supplied, instead deletes any existing autoreply for the author.

#### wb autoreply clear [user]

Owner only. Clears a given user's autoreply setting.

#### wb autoreply list

Owner only. Lists all existing autoreplies for every user.

### wb tally (emotehistory)

#### wb tally emotes [channel] [after_date] ([endRange])

Counts custom emote usage for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

#### wb tally reactions [channel] [after_date] ([endRange])

Counts custom emote usage as reactions for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

#### wb tally all [channel] [after_date] ([endRange])

Sums custom emote usage and reactions for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

#### wb tally everything [after_date] ([endRange])

Owner only. Sums all custom emote usage and reactions for all messages in all channels *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

### errorhandler

This cog is unchanged from the template and has no user commands. It facilitates error reporting to Discord users by sending a Discord message when the bot encounters an error.

### moderate

This cog is highly specialized for Dedotated waam. We have a text channel called #babe-wake-up for sharing serious long-form videos. Discussions on these videos can be pervasive in the channel, so in order to keep it a vanilla catalogue of interesting videos, the bot will yell at users who make top-level messages with no link. The bot will then encourage the offending user to move their thoughts to a thread.

### reprimand

Shame system for misbehaving users. Stores history of reprimanding in a mongo database. The log of reprimands can be queried, so the shame is eternal. Unless the shame is cleared, useful if reprimands are generated in bad faith.

#### wb reprimand [user] ([reason])

Adds a reprimand for the given user. Can optionally add a text description of a "reason" for the reprimanding, which can be revisited if that particular user is included in `wb reprimand list [user]`.

#### wb reprimand [list] ([user])

Prints the reprimand log to Discord. This will show who has been reprimanded the most, but rest assured that even the smallest reprimandees will not be spared the humiliation. Optionally include a user argument which will print all reprimands that have a reason attached, so they can rehash their misgivings.

### sample

#### wb test

Owner only. This command tests that the bot is online and configured properly.

### schedule

Scrapes ESPN's schedule page for most sports leagues, displaying the most relevant upcoming/live/finished games and their results, or times and TV programming.

#### wb schedule [league_name]

Scrapes ESPN for the given league's schedule. Accepts many aliases and slang for various leagues. Covers any televised American Pro or College sport.

### yahoo

Upcoming integration with the Yahoo Fantasy Sports API via https://github.com/uberfastman/yfpy with extra special ESPN Fantasy API integration to acquire projections and NFL scheduling data.