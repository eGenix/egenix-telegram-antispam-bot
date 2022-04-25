#!/usr/bin/env python3

""" eGenix Antispam Bot for Telegram Runtime

    For using the package directly without helper modules:

    > python3 -m telegram_antispam_bot

    Simply configure everything via env variables.

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
# Fix sys.argv[0], since pyrogram uses this to detect the workdir
# instead of using os.getcwd() for some reason.
import sys
import os
sys.argv[0] = os.path.join(os.getcwd(), 'dummy')
#print (f'Module start: sys.argv={sys.argv!r}, CWD={os.getcwd()!r}')

# Run a single bot
from telegram_antispam_bot.antispam_bot import AntispamBot
app = AntispamBot()
app.run_bot()
