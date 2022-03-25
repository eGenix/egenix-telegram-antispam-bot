#!/usr/bin/env python3

""" eGenix Antispam Bot for Telegram Runtime

    For using the package directly without helper modules:

    > python3 -m telegram_antispam_bot

    Simply configure everything via env variables.

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
from telegram_antispam_bot.antispam_bot import AntispamBot

# Run a single bot
app = AntispamBot()
app.run_bot()
