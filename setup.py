#!/usr/bin/env python3

""" eGenix Anti Spam Bot for Telegram

    Package configuration file.

    Written by Marc-Andre Lemburg in 2022.
    Copyright (c) 2022, eGenix.com Software GmbH; mailto:info@egenix.com
    License: MIT
"""
import sys
import types
from setuptools import setup
from telegram_antispam_bot import __version__

# Load file data
with open('README.md', encoding='utf-8') as f:
    _long_description = f.read()

# Prepare meta data
class metadata:
    name='egenix-telegram-antispam-bot'
    version=__version__
    description='eGenix Antispam Bot for Telegram'
    long_description=_long_description
    long_description_content_type = 'text/markdown'
    license='MIT'
    author='eGenix.com Software, Skills and Services GmbH'
    author_email='info@egenix.com'
    maintainer='eGenix.com Software, Skills and Services GmbH'
    maintainer_email='info@egenix.com'
    url='https://github.com/egenix/egenix-telegram-antispam-bot'
    # See https://pypi.org/classifiers/ for possible values:
    classifiers = [
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        #"License :: Freely Distributable",
        #"License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        #"Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        #"Operating System :: MacOS",
        #"Operating System :: Other OS",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities ",
        "Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        ]
    install_requires=[
        'Pyrogram ~=1.4',
        'TgCrypto ~=1.2',
    ]
    python_requires='>=3.9'
    packages=[
        'telegram_antispam_bot',
    ]
    package_data={
        'telegram_antispam_bot': ['README.md', 'LICENSE'],
    }
      
    @classmethod
    def _dict(cls):
        return {
            k:v
            for (k, v) in cls.__dict__.items()
            if k[0] != '_'}

# Run setup
if __name__ == '__main__':
    setup(**metadata._dict())
