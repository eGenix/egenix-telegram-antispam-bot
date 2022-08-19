#!/usr/bin/env python3

""" eGenix Antispam Bot for Telegram Challenges

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
import random
import re

from telegram_antispam_bot.config import (
        CHALLENGE_CHARS,
        CHALLENGE_LENGTH,
        DEBUG,
)

### Globals

# Debug level
_debug = DEBUG

### Challenge class

class Challenge:

    """ Challenge for the user to answer correctly.

        The base implementation simply creates a short text snippet,
        which the user will have to enter. Case does not matter.

        Other implementations are possible, provided the API is kept
        compatible.

    """
    # Client using this Challenge instance
    client = None

    # Characters to use for challenge strings
    challenge_chars = CHALLENGE_CHARS

    # Length of challenge strings
    challenge_length = CHALLENGE_LENGTH

    # Expected answer as regular expression
    answer = ''

    def __init__(self, client, message):

        """ Create a challenge instance.

            client has to point to the AntispamBot instance.
            message needs to point to the member's signup message and
            can be used for creating the challenge.

            Note: message should not be stored in the instance to avoid
            creating circular references.

        """
        self.client = client

    def create_challenge(self, message):

        """ Create a challenge text to send to the user and the expected answer.

            Returns (challenge, answer).

        """
        answer = ''.join(
            random.choices(
                self.challenge_chars,
                k=self.challenge_length)).upper()
        return (
            f'`{answer}`', # we format this verbatim to make it easier to spot
            f'(?i)^{answer}$' # case is not important for the answer
        )

    async def send(self, message):

        """ Send a message to the new user, asking to answer a
            challenge.

            message needs to point to the member's signup message.
            client has to point to the AntispamBot instance.

        """
        # Create challenge text and answer
        challenge, self.answer = self.create_challenge(message)
        # Send challenge string
        message.conversation.append(
            await self.client.send_message(
                message.chat.id,
                f'Welcome to the chat, {message.new_member.first_name} ! '
                f'Please enter {challenge} into this chat '
                f'to get approved as a member '
                f'(within the next few seconds).',
                reply_to_message_id=message.message_id))

    def check(self, answer):

        """ Check the user's answer to the challenge and return
            True/False depending on whether it matches or not.

            answer needs to point to the user's answer message.

        """
        # Entered value
        value = answer.text.strip()
        # Check against snippet
        if _debug:
            self.client.log(f'Checking entered value {value!r} against {self.answer}')
        if re.match(self.answer, value) is not None:
            return True
        return False

class UppercaseChallenge(Challenge):

    """ Enter all uppercase chars as challenge.
    """
    def create_challenge(self, message):

        lower = random.choices(
            self.challenge_chars.lower(),
            k=self.challenge_length)
        upper = random.choices(
            re.sub('[^A-Z]+', '', self.challenge_chars.upper()),
            k=self.challenge_length)
        challenge = lower + upper
        random.shuffle(challenge)
        answer = [x for x in challenge if x.isupper()]
        return (
            f'all uppercase characters found in `{"".join(challenge)}`',
            f'(?i)^{"".join(answer)}$'
        )

class ReverseStringChallenge(Challenge):

    """ Reverse a string as challenge.
    """
    def create_challenge(self, message):

        challenge = random.choices(
            self.challenge_chars.upper(),
            k=self.challenge_length)
        answer = reversed(challenge)
        return (
            f'the reversed version of the string `{"".join(challenge)}`',
            f'(?i)^{"".join(answer)}$'
        )

class MathAddChallenge(Challenge):

    """ Solve a math addition as challenge.
    """
    def create_challenge(self, message):

        a = random.randint(1, 100)
        b = random.randint(1, 100)
        return (
            f'the result of `{a} + 2 * {b}`',
            f'^{str(a + 2 * b)}$'
        )

class MathMultiplyChallenge(Challenge):

    """ Solve a math multiplication as challenge.
    """
    def create_challenge(self, message):

        a = random.randint(1, 100)
        b = random.randint(1, 100)
        return (
            f'the result of `{a} * {b} + 2`',
            f'^{str(a * b + 2)}$'
        )

class ListItemChallenge(Challenge):

    """ Figure out Python list indexing as challenge.
    """
    def create_challenge(self, message):

        l = random.sample(range(10), k=6)
        i = random.randint(0, 5)
        return (
            f'the result of the Python expression `{l!r}[{i}]`',
            f'^{str(l[i])}$'
        )
