# Docker file for the regbot python container
FROM python:3.10

# Upgrade System:
RUN apt-get update && apt-get -y upgrade && apt-get -y autoremove

# Download and install dependencies
#RUN apt-get install -qq build-essential libssl-dev libxrender-dev wget git wkhtmltopdf

# Our Docker commands:
RUN mkdir -p /var/lib/tgbot
WORKDIR /var/lib/tgbot

# Install software
RUN pip3 install egenix-telegram-antispam-bot
