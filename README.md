# Waambot: A Discord bot for denizens of the Dedotated waam Discord Server

This bot was spawned from a template written in Python to develop a Discord bot and deploy via Docker container. 

The template is available at https://github.com/MoonlightCapital/discord-py-template

## Getting Started:

- See [Mongo on Dockerhub](https://hub.docker.com/_/mongo) to get a database container running
- See [the install page](installing.md) to get the bot's code and run it in a container

For the Yahoo Fantasy Football Module:

- See https://github.com/uberfastman/yfpy to get connected to the Yahoo Fantasy API
- See https://github.com/cwendt94/espn-api to get connected to the ESPN Fantasy API (for projections and NFL schedule/scores)


## Modules (Cogs):

***
### archive

These commands are capable of recording an entire Discord text channel locally on the machine that is running the bot. I assigned it to a volume in `docker-compose.yml` to store the archives, so that a new prospective bot owner can easily set that location.

#### wb archive

Owner only. Records text log history of this channel onto the bot's storage. Attachments are skipped, but links remain. 

#### wb archive all

Owner only. Records entire history of this channel onto the bot's storage. All images are downloaded and the text log is saved.

***
### autoreply

Facilitate setting an out-of-office sort of message. The bot will automatically reply to users who tag somebody with an autoreply message set. The bot owner is also able to visualize and/or clear existing autoreplies for a user if they need to be blown away.

#### wb autoreply

Sets up or modifies an autoreply message for the command author. If no message is supplied, instead deletes any existing autoreply for the author.

#### wb autoreply clear [user]

Owner only. Clears a given user's autoreply setting.

#### wb autoreply list

Owner only. Lists all existing autoreplies for every user.

***
### tally (emotehistory)

#### wb tally emotes [channel] [after_date] ([endRange])

Counts custom emote usage for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

#### wb tally reactions [channel] [after_date] ([endRange])

Counts custom emote usage as reactions for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

#### wb tally all [channel] [after_date] ([endRange])

Sums custom emote usage and reactions for all messages in a given channel *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

#### wb tally everything [after_date] ([endRange])

Owner only. Sums all custom emote usage and reactions for all messages in all channels *after* a given date. Can limit the date range with an optional end date. Dates must be %m/%d/%y (say, 4-25-22)

***
### errorhandler

This cog is unchanged from the template and has no user commands. It facilitates error reporting to Discord users by sending a Discord message when the bot encounters an error.

***
### moderate

This cog is highly specialized for Dedotated waam. We have a text channel called #babe-wake-up for sharing serious long-form videos. Discussions on these videos can be pervasive in the channel, so in order to keep it a vanilla catalogue of interesting videos, the bot will yell at users who make top-level messages with no link. The bot will then encourage the offending user to move their thoughts to a thread.

***
### reprimand

Shame system for misbehaving users. Stores history of reprimanding in a mongo database. The log of reprimands can be queried, so the shame is eternal. Unless the shame is cleared, useful if reprimands are generated in bad faith.

#### wb reprimand [user] ([reason])

Adds a reprimand for the given user. Can optionally add a text description of a "reason" for the reprimanding, which can be revisited if that particular user is included in `wb reprimand list [user]`.

#### wb reprimand [list] ([user])

Prints the reprimand log to Discord. This will show who has been reprimanded the most, but rest assured that even the smallest reprimandees will not be spared the humiliation. Optionally include a user argument which will print all reprimands that have a reason attached, so they can rehash their misgivings.

***
### sample

#### wb test

Owner only. This command tests that the bot is online and configured properly.

***
### schedule

Scrapes ESPN's schedule page for most sports leagues, displaying the most relevant upcoming/live/finished games and their results, or times and TV programming.

#### wb schedule [league_name]

Scrapes ESPN for the given league's schedule. Accepts many aliases and slang for various leagues. Covers any televised American Pro or College sport.

***
### ff (yahoo, fantasy)

Upcoming integration with the Yahoo Fantasy Sports API via https://github.com/uberfastman/yfpy with extra special ESPN Fantasy API integration to acquire projections and NFL scheduling data.

#### wb ff test

Registered users only. Bot outputs a line to signal that the yahoo module has loaded.

#### wb ff register [team_number]

Assigns the user to a team in the league. The league can be displayed with `wb ff league` to find the number for your team. The record is stored in a mongo db running in another Docker container.

#### wb ff unregister

Removes the user from the database of Fantasy Managers (only removes records that correspond with the currently active league id, this module is not really designed well for use with multiple leagues).

#### wb ff league

Prints the teams in the currently active Yahoo Fantasy Football League. This is the primary method for discerning a team id number for use with `wb ff register`

#### wb ff standings

Prints the latest standings for the currently active League.

#### wb ff scoreboard ([week])

Prints the latest week's scoreboard in a new thread. This output is threaded because it is quite a bit of information. My server takes about 20 seconds to run this command because of the quantity of API calls and the amount of string manipulation involved. Optional integer week parameter to specify a certain week's scoreboard during the current year.

The user for this command must be registered with `wb ff register`, because it takes a fair amount of server resources and also clutters the channel with a thread when invoked.

#### wb ff matchups ([week])

Prints the matchups for the current week (just the team/manager pairings). Used to discern matchup id number for use with `wb ff matchup`. Optional week parameter to retrieve matchup numbers for past or future weeks.

#### wb ff matchup ([matchup_number]) ([week])

Prints the user's matchup for the current week. Optional matchup id parameter allows the user to view others' matchups. Additionally, an optional week parameter allows specifying matchups from past/future weeks, although cannot be used without the matchup_number.

#### wb ff team ([team_number]) ([week])

Prints the user's team for the current week. Providing a team_number parameter can show a different team in the league. Providing a week will show that team's lineup during a certain week.