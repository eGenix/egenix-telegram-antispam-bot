#!/usr/bin/env python3

""" eGenix Antispam Bot for Telegram Configuration

    The values in this module can be overridden using a module
    "local_config" or by providing OS environment variables of the same
    name with "TG_" prefix, e.g. export TG_SESSION_NAME="mybot".

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
 """
import telegram_antispam_bot.config_helpers as _tools

# Name of the client session
#
# WARNING: pyrogram will save auth data in a SQLite database using this name
# in the local dir, so make sure the permissions are set to not leak the
# credentials.
#
SESSION_NAME = 'antispambot'

# Mode to use for protecting the session database
SESSION_DATABASE_MODE = 0o600

# Management group ID, or 0 (don't use such a group)
MANAGEMENT_GROUP_ID = 0

# Moderation groups. Comma separated set of group IDs to moderate. If
# empty, the bot will work on any group it was added to.
MODERATION_GROUP_IDS = _tools.IntFrozenSet()

# Idle loop interval in seconds. Idle processing will happen at these
# intervals.
IDLE_INTERVAL = 10

# Response timeout in seconds. The timer starts when the user enters the
# chat and resets whenever the user enters something.
RESPONSE_TIMEOUT = 120

# Reminder time in seconds. A reminder to enter something is sent after
# these many seconds.
REMINDER_TIME = 60

# Ban time in seconds. Set to 0 to make bans permanent.
BAN_TIME = 3600 # one hour

# Time to show the rejection notice
REJECT_NOTICE_TIME = 10

# Debug level
DEBUG = 0

# Log file. Use "stdout" to have the log write to the console.
LOG_FILE = 'stdout'

### Telegram API

# API access. You can get these from
# https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
#
# See https://docs.pyrogram.org/faq/why-is-the-api-key-needed-for-bots
# for why these are needed. In short: pyrogram doesn't use the TG Bot
# API, but instead talks directly to the TG API.
#
# If you don't want to keep the API credentials on the server, you can
# have the installation process run the bot once with the correct
# credentials and then set these to dummy values in the config. They are
# only needed during the auth process.
#
API_ID = '123'
API_HASH = '123'

# Bot token. The @BotFather will provide this.
# See https://core.telegram.org/bots#3-how-do-i-create-a-bot
BOT_TOKEN = '123'

### Challenges

# Characters to use for challenge strings; try to leave out chars which
# look ambiguous, e.g. 0 and O, 1 and I. The default challenge
# implementation matches these case-insensitive.
CHALLENGE_CHARS = 'abcdefghjklmnpqrstuvwxyz23456789'

# Length of challenge strings
CHALLENGE_LENGTH = 4

# Set of Challenge classes to use for the Bot
CHALLENGES = _tools.StrFrozenSet(['Challenge'])

# Max. number of failed challenge responses to allow
MAX_FAILED_CHALLENGES = 3

### Customization

# Override default values with custom ones from a local module
try:
    from local_config import *
except ImportError:
    pass

# Replace values defined in the module with OS environment field values
# where available.
_tools.os_env_override(globals(), prefix='TG_')
