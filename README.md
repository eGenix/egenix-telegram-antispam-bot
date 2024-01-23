# eGenix Antispam Bot for Telegram

This bot package provides a simple, yet effective way to deal with spam
signups to [Telegram Messenger](https://telegram.org/) (TG) groups.
Unfortunately, these have grown to a level that is not manually
manageable anymore (see [Motivation](#motivation) below for details).

## Features

- Low impact mode of operation: the bot tries to keep noise in the group
  to a minimum
- Several challenge mechanisms to choose from, more can be added as
  needed
- Flexible and easy to use configuration
- Only needs a few MB of RAM, so can easily be put into a container or run
  on a Raspberry Pi
- Can handle quite a bit of load due to the async implementation

## Requirements

- Python 3.9+
- [pyrogram](https://github.com/pyrogram/pyrogram) package (see
  requirements.txt)
- only tested on Linux

## Preparation

In order to run the bot and connect it to your TG group(s), you will
first have to get API tokens from TG. Please see
https://core.telegram.org/api/obtaining_api_id#obtaining-api-id for
details on how to obtain the two credentials API ID and hash.

⚠️ The API credentials are bound to the TG account you create them with and
can be used to even delete the account, so keep them safe.

Next, you need to register a bot with TG. This can be done by chatting
with the TG BotFather. See
https://core.telegram.org/bots#3-how-do-i-create-a-bot for details. The
BotFather will send you a Bot token.

## Installation

It is best to install the bot inside a
[venv](https://docs.python.org/3/library/venv.html). You can use the
virtual env tool of your choice to set this up.

Then install the [PyPI
package](https://www.egenix.com/library/telegram-antispam-bot/), using
pip:

```bash
pip3 install telegram_antispam_bot
```

### Installation using Docker

If you want to run the bot using Docker, have a look at the `docker/`
subdir in the source distribution. After configuring the bot in
`docker/config/tgbot_env` you can then run the bot by running:

```bash
cd docker/
docker-compose up -d
```

Be sure to check the logs using ``docker-compose tgbot logs`` for any
errors that may occur. You can also without "-d" (no detach) to see the
logs written to the console for testing purposes.

## Configuration

The simplest way to configure the bot is via OS environment variables
(env vars), but you can also put the configuration into a Python module
`local_config.py` which Python can find on the sys.path. See
`telegram_antispam_bot/config.py` for details.

We'll go with the env var approach. All env vars use the prefix "TG_" to
avoid getting in the way with other env vars.

The most important variables to set are these:

- `TG_API_ID`: Use the API ID you received from TG.

- `TG_API_HASH`: Use the API hash you received from TG. This is secret
  information.

- `TG_BOT_TOKEN`: Use the Bot token you received from the BotFather.  This
  is secret information.

- `TG_SESSION_NAME`: Session database name to use. Defaults to
  'antispambot'. You only need to set this in case you plan to run
  multiple bot instances from the same directory.

### Limiting the attack surface

You only need to pass in the real values of the authentication env vars
when first authenticating against the TG API.

The underlying pyrogram package will store the session credentials in a
SQLite database (named after `TG_SESSION_NAME`).

Once this is in place, the secrets can be replaced with dummy values or
left unset. Do take care to protect the session database, since this can
be used to hijack TG sessions. The bot will enforce file permissions
upon startup.

### Additional settings

You can also specify a few other env vars to further customize the
installation:

- `TG_MANAGEMENT_GROUP_ID`: Set this to the TG ID of the group you want to
  use for receiving admin log messages. The bot will have to be made
  member of this group. The bot will always log these messages to
  stdout.

- `TG_MODERATION_GROUP_IDS`: Set this to a comma separated set of group
  IDs to moderate. If not set, the bot will moderate all groups it gets
  added to as an admin.

- `TG_DEBUG`: Set this to 1 to get debug messages, which will include
  details about the messages sent to chats the bot is listening on.

- `TG_CHALLENGES`: Set this to a comma separated list of Challenge
  subclass names found in `telegram_antispam_bot/challenge.py`. The bot
  will then pick one of these randomly when sending a challenge.

Getting the group IDs is not easy from the TG clients, but you can use
the `TG_DEBUG` setting to find out the IDs. The log will show entries
such as `chat=pyrogram.types.Chat(id=1234, type='supergroup',
...` when writing messages into the group chat. In this example, the
group ID to use is 1234.

It is usually best to configure the extra settings after getting the
initial setup up and running.

For more details regarding the configuration and additional settings,
please have a look at the `telegram_antispam_bot/config.py` file.

## Running the Bot

You can run the bot inside a container, as a service on a root server or
VM, or manually from the command line.

If you've setup the configuration via OS environment variables, all you
need to do is run the package:

```bash
python3 -m telegram_antispam_bot
```

## Adding the Bot to a TG Group

In order for the bot to work on a group, you will have to add it as an
admin to the group. It needs the permissions *Delete messages* and *Ban
users*. The other permissions can be disabled.

## Bot commands

Unlike other TG bots, this bot does not implement any bot commands (e.g.
there is no '/help').

Experience has shown that implementing such commands often leads to
group members trying to interact with the bot, even though they don't
have permission to do anything. This usually creates enough noise to
make the bot operation less useful.

## How it works

The bot will recognize new group signups and ask the new users to enter
a challenge string within a certain time frame. Correctly entering the
challenge then accepts the new user. Not entering the challenge in time
results in a ban. The same happens, if the user enters too many wrong
answers.

The bot / user conversation is mostly deleted after either successful or
failed signup to keep the noise level low.

## FAQ

- I see connection error messages in the logs. Are those something to worry about ?

  > No, the underlying pyrogram library will automatically try to
    reconnect. You should only dig deeper in case you notice that the
    bot is not reacting to new signups.

- I changed the configuration. Will the bot automatically detect those changes ?

  > No, you will have to restart the bot for the changes to take affect.

- Will restarting the bot have a negative effect ?

  > A short downtime is not much of a problem. If you restart the bot
    while it is talking to a new signup, you will have to do manual
    cleanup of the chat, since the conversations are not stored in the
    database.

- I don't want to monitor a log file. Can I point the bot to an admin TG group ?

  > Yes, you can set up a TG admin group, make the bot a (regular) member
    and then add the ID of the group as `TG_MANAGEMENT_GROUP_ID`.

## Motivation

eGenix has long been running a local user group meeting in Düsseldorf
called Python Meeting Düsseldorf and we have been using a Telegram group
for group communication.

In the early days, the group worked well and we only had few spammers
joining it, which we could well handle manually. More recently, this has
changed dramatically. We are seeing between 2-5 spam signups per day,
often at night. Furthermore, the signups accounts are not always easy to
spot as spammers, since they often come with profile images,
descriptions, etc.

With the bot, we now have a more flexible way of dealing with the
problem.

## License

MIT

## Contributions

We welcome contributions and will integrate them after review via the
usual PR process, provided they are MIT licensed as well.

## Credits / Notices

- Thanks go out to [Dan](https://github.com/delivrance) for creating the
wonderful [pyrogram](https://github.com/pyrogram/pyrogram) async TG
package.

- "Telegram" is a trademark of Telegram LLC.

## Resources

- [eGenix Antispam Bot for Telegram home page](https://www.egenix.com/library/telegram-antispam-bot/)
- [eGenix Antispam Bot for Telegram on Github](https://github.com/egenix/egenix-telegram-antispam-bot)
- [pyrogram](https://github.com/pyrogram/pyrogram), the TG library used
  by this bot

## Changelog

- 0.6.0:
  - Upgraded to pyrogram 2.0.106, which fixes a weird error we have been
    getting recently with the old version 1.4.16 (see
    https://github.com/pyrogram/pyrogram/issues/1347)
  - Catch weird error from Telegram when deleting conversations; this
    seems to sometimes fail, probably due to a glitch on their side
  - Made the math and char entry challenges a little harder
  - Added new DictItemChallenge

- 0.5.0:
  - Output version number when starting up the bot
  - Added more PyPI project links
  - Upgraded TgCrypto
  - Added support for muting the bot messages and enabled this per
    default; thanks to Alexander Ananchenko for bringing up that idea
  - Added support for also removing the approval message after a timeout
    (not enabled per default);  thanks to Alexander Ananchenko for that
    idea
  - Bot conversations are now logged before removing them; this makes it
    easier to debug challenges (some may be too easy)

- 0.4.0:
  - Added new challenge MathMultiplyChallenge
  - Made the MathAddChallenge and MathMultiplyChallenge a little more
    difficult

- 0.3.0:
  - Added new challenge ListItemChallenge
  - Added new config variables MAX_FAILED_CHALLENGES to limit the number
    of failed challenge responses. Defaults to 3.
  - Added docker-compose config example to sources
  - Fixed display of the user name to always show the full name, where
    available.
  - Added work-around for pyrogram to not create session files inside
    the package dir when running the bot in -m mode
  - Fixed bug to make file logging work
  - Fixed bug in ban time handling; this now works correctly

- 0.2.0: Initial release on PyPI

- 0.1.0: Initial release on Github


Enjoy, \
*Marc-André Lemburg* \
[eGenix.com](https://egenix.com/)
