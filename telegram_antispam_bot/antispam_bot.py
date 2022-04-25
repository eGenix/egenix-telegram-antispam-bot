#!/usr/bin/env python3

""" eGenix Antispam Bot for Telegram

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
import encodings
import os
import asyncio
import random
import time
import copy
import pprint
import logging
import datetime
from pyrogram import Client, handlers
from pyrogram.types import Message

from telegram_antispam_bot import challenge

# Load configuration
from telegram_antispam_bot.config import (
    DEBUG,
    LOG_FILE,
    IDLE_INTERVAL,
    SESSION_NAME,
    SESSION_DATABASE_MODE,
    MANAGEMENT_GROUP_ID,
    MODERATION_GROUP_IDS,
    IDLE_INTERVAL,
    RESPONSE_TIMEOUT,
    REMINDER_TIME,
    BAN_TIME,
    REJECT_NOTICE_TIME,
    API_ID,
    API_HASH,
    BOT_TOKEN,
    CHALLENGES,
    MAX_FAILED_CHALLENGES,
    )

### Globals

# Debug level
_debug = DEBUG

# Singleton
NotGiven = object()

### Logging

# Configure logging
if LOG_FILE != 'stdout':
    # File logging
    logging.basicConfig(
        filename=LOG_FILE,
        encoding='utf-8',
        format='%(asctime)s.%(msecs)03d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        #level=logging.INFO, # useful for pyrogram debugging
    )
else:
    # stdout logging
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        #level=logging.INFO, # useful for pyrogram debugging
    )

# Log object
LOG = logging.getLogger('antispambot')
LOG.setLevel(logging.INFO)

### Helpers

def full_name(member, full_info=False):

    """ Return the full name of the member.

        If full_info is true (default is False), a markdown version is
        returned, which includes a link to the user account, the
        username and the ID.

    """
    # Deal with None entries gracefully
    first_name = member.first_name or ''
    last_name = member.last_name or ''
    if first_name and last_name:
        name = first_name + ' ' + last_name
    elif first_name:
        name = first_name
    elif last_name:
        name = last_name
    else:
        name = '(missing name)'
    if not full_info:
        return name
    return (
        f'["{name}" '
        f'(username={member.username}, id={member.id})]'
        f'(tg://user?id={member.id})')

### Bot class

class AntispamBot(Client):

    # Dictionary of new members signing up to the group.
    #
    # The dict maps member IDs to the initial new member message.
    new_members = None

    # Flag to keep the .idle_loop() alive
    keep_running = False

    # Bot user id. Set in .start()
    bot_id = 0

    # Set of Challenge class names to use
    challenges = CHALLENGES

    # Challenge classes to use. Set in .__init__(), based on .challenges
    challenge_classes = None

    # Max. number of failed challenge responses to allow
    max_failed_challenges = MAX_FAILED_CHALLENGES

    # Group to use for management messages
    management_group_id = MANAGEMENT_GROUP_ID

    # Set of group chat IDs to respond to. If empty or None, no
    # restrictions are applied.
    moderation_group_ids = MODERATION_GROUP_IDS

    # Idle loop interval in seconds. Idle processing will happen at these
    # intervals.
    idle_interval = IDLE_INTERVAL

    # Response timeout in seconds. The timer starts when the user enters the
    # chat and resets whenever the user enters something.
    response_timeout = RESPONSE_TIMEOUT

    # Reminder time in seconds. A reminder to enter something is sent after
    # these many seconds.
    reminder_time = REMINDER_TIME

    # Ban time in seconds. Set to 0 to make bans permanent.
    ban_time = BAN_TIME

    # Time to show the rejection notice
    reject_notice_time = REJECT_NOTICE_TIME

    ### Event loop

    def __init__(
        self,
        session_name=SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        management_group_id=None,
        moderation_group_ids=None,
        challenges=None,
        ):
        super().__init__(
            session_name,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token)
        if management_group_id is not None:
            self.management_group_id = management_group_id
        if moderation_group_ids is not None:
            self.moderation_group_ids = moderation_group_ids

        # Configure available Challenge classes
        if challenges is not None:
            self.challenges = challenges
        l = []
        for class_name in self.challenges:
            cls = getattr(challenge, class_name, None)
            if cls is not None and issubclass(cls, challenge.Challenge):
                l.append(cls)
        self.challenge_classes = l

    def run_bot(self):
        self.run(self.main_loop())

    async def main_loop(self):
        self.keep_running = True
        async with self:
            # Protect the SQLite session database
            try:
                os.chmod(self.storage.database, SESSION_DATABASE_MODE)
            except FileNotFoundError as error:
                self.log(
                    f'WARNING: Could not secure session database file: '
                    f'{error}')
            # Run idle loop
            await self.idle_loop()

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.bot_id = me.id
        self.log(f'Starting up ...')

        if _debug > 1:
            self.log(
                f'Using API ID {self.api_id!r} and Hash '
                f'{self.api_hash!r}')

        # Setup vars
        self.new_members = {}

        # Add catch all handler
        self.add_handler(
            handlers.MessageHandler(self.all_messages))

        await self.log_admin(f'Started Antispam Bot "<b>{me.username}</b>"')

    async def idle_loop(self):
        while self.keep_running:
            await asyncio.sleep(self.idle_interval)
            if _debug > 1:
                self.log(f'Running idle checks')
          # Check new members every now and then
            if self.new_members:
                await self.check_new_members()

    async def stop(self):
        me = await self.get_me()
        await self.log_admin(f'Stopping Antispam Bot "<b>{me.username}</b>"')
        await super().stop()

    # Handlers

    async def all_messages(self, client, message):

        """ Handler which receives all messages sent to the chat.

            This delegates the handling to other methods.
        """
        if _debug:
            self.log('New message:', message)
        if not self.check_access(message):
            return

        # Ignore messages without a .from_user attribute
        if not message.from_user:
            return
        member_id = message.from_user.id

        # Ignore messages sent by the bot itself
        if member_id == self.bot_id:
            return

        # Delegate some messages to other handlers:
        if message.new_chat_members:
            # Process new chat members message
            return await self.new_chat_members(client, message)

        # Check for answers to welcome questions
        if member_id in self.new_members:
            signup_message = self.new_members[member_id]
            signup_message.conversation.append(message)

            if message.text:
                # Process text answer from new member
                signup_message.timer = time.time()
                if signup_message.challenge.check(message):
                    # Correct answer
                    await self.welcome_new_member(signup_message)
                else:
                    # Failure
                    await self.failed_challenge(signup_message, message)
            else:
                # Ignore other types of messages, e.g. stickers, photos, etc.
                pass

    async def new_chat_members(self, client, message):

        """ Handler for new chat members messages.

            Initiates the challenge/response conversation with the user.
        """
        if _debug:
            self.log('New chat members:', message)
        if not self.check_access(message):
            return

        # Set up everything for the welcome question processing, with
        # one message copy per new chat member
        for new_member in message.new_chat_members:
            signup_message = copy.copy(message)
            signup_message.new_chat_members = [new_member]
            signup_message.new_member = new_member
            signup_message.conversation = []
            signup_message.member_banned = False
            signup_message.reminder_sent = False
            signup_message.timer = 0
            signup_message.failed_challenges = 0
            self.new_members[new_member.id] = signup_message
            await self.send_challenge(signup_message)

    # Helpers

    async def log_admin(self, text):

        """ Log an admin text message to the management group.
        """
        self.log(text)
        if not self.management_group_id:
            return
        await self.send_message(
            self.management_group_id,
            text)

    def log(self, text=None, object=NotGiven, level=logging.INFO):

        """ Log a text and/or an object at the given level.

            The object is pretty-printed, if given.
        """
        if text is not NotGiven:
            LOG.log(level, text)
        if object is not NotGiven:
            LOG.log(level, pprint.pformat(object))

    def check_access(self, message):

        """ Check whether we should process the message or not.
        """
        chat_id = message.chat.id
        if chat_id == self.management_group_id:
            # Don't process messages from the management group
            return False
        if self.moderation_group_ids:
            if chat_id not in self.moderation_group_ids:
                # Invalid access
                return False
        return True

    def create_challenge(self, message):

        """ Return a Challenge instance to use for the challenge.
        """
        cls = random.choice(self.challenge_classes)
        return cls(self, message)

    async def send_challenge(self, message):

        """ Send a challenge message to the user.

            message needs to point to the user's signup message.
        """
        new_member = message.new_member
        challenge = self.create_challenge(message)
        message.challenge = challenge
        await challenge.send(message)
        message.timer = time.time()
        await self.log_admin(
            f'Processing application by '
            f'{full_name(new_member, full_info=True)} '
            f' to group "<b>{message.chat.title}</b>"'
            )

    async def send_reminder(self, message):

        """ Send a reminder in case the member is not responding to the
            challenge.

            message needs to point to the member's signup message.
        """
        chat_id = message.chat.id
        new_member = message.new_member
        message.conversation.append(
            await self.send_message(
                chat_id,
                f'Reminder: We are still waiting for an answer from user '
                f'"{full_name(new_member)}".'))
        message.reminder_sent = True

    async def failed_challenge(self, message, reply_to_message):

        """ Deal with a failed challenge response.

            The user can try again within the response timeout.

            message needs to point to the user's signup message.
            reply_to_message needs to be the message with the user's
            answer.

        """
        message.failed_challenges += 1
        message.conversation.append(
            await self.send_message(
                message.chat.id,
                f'I am sorry, but this answer is not correct. '
                f'Please try again.',
                reply_to_message_id=reply_to_message.message_id))

    async def remove_conversation(self, message):

        """ Remove the welcome conversation with the user from the chat.

            message needs to point to the user's signup message.
        """
        # Note: some entries in the .conversation may be simple booleans
        # in case messages could not be sent, so we skip those
        message_ids = [
            message.message_id
            for message in message.conversation
            if isinstance(message, Message)]
        # Remove the new user message as well, if the user was banned
        if message.member_banned:
            message_ids.insert(0, message.message_id)
        await self.delete_messages(message.chat.id, message_ids)

    async def welcome_new_member(self, message):

        """ Accept and welcome the user as a new member to the group.

            This concludes the conversation and removes the member from
            the .new_members dict.

            message needs to point to the user's signup message.
        """
        chat_id = message.chat.id
        new_member = message.new_member
        await self.remove_conversation(message)
        await self.send_message(
            chat_id,
            f'Thank you for answering the welcome question, '
            f'{full_name(new_member)}. '
            f'You are now a member of the chat. '
            f'Please introduce yourself to the group in a line or two.')
        self.new_members.pop(new_member.id)
        await self.log_admin(
            f'Accepted application by '
            f'{full_name(new_member, full_info=True)}'
            )

    async def reject_application(self, message):

        """ Reject an application after a failed conversation.

            message needs to point to the member's signup message.
        """
        chat_id = message.chat.id
        new_member = message.new_member
        message.conversation.append(
            await self.send_message(
                chat_id,
                f'User "{full_name(new_member)}" failed to answer '
                f'in time. Bye !'))
        ban_until = (
            datetime.datetime.now() +
            datetime.timedelta(seconds=self.ban_time))
        message.conversation.append(
            await self.ban_chat_member(
                chat_id, new_member.id, until_date=int(ban_until.timestamp())))
        message.member_banned = True
        self.new_members.pop(new_member.id)
        await self.log_admin(
            f'Banned '
            f'{full_name(new_member, full_info=True)} '
            f' from group "<b>{message.chat.title}</b>"'
            f' for {self.ban_time} seconds (until {ban_until})'
            )
        await asyncio.sleep(self.reject_notice_time)
        await self.remove_conversation(message)

    # Loop processing

    async def check_new_members(self):

        """ Check new member applications.

            This sends reminders or rejects their application in case of
            timeouts.
        """
        current_time = time.time()
        if _debug:
            self.log(f'Checking new members')
        for id, message in list(self.new_members.items()):
            if not message.timer:
                # Challenge not yet sent
                continue
            waiting_time = current_time - message.timer
            if (waiting_time > self.response_timeout or
                message.failed_challenges >= self.max_failed_challenges):
                # Ban member for a while
                await self.reject_application(message)
            elif (not message.reminder_sent and
                  waiting_time > self.reminder_time):
                # Send a reminder message
                await self.send_reminder(message)
            else:
                if _debug:
                    self.log(
                        'Still waiting for answer from new member:',
                        message)

###

if __name__ == '__main__':
    app = AntispamBot(
        session_name=SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )
    app.run_bot()
