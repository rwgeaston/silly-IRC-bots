#! /usr/bin/env python
# 
# srjbot
#
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

import threading
import random
from datetime import date, datetime
import time
import urllib2, re

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server='irc.rd.tandberg.com', port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.nickname = nickname

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        a = e.arguments[0]
        self.check_and_answer(e, a)
        return
    
    def message(self, message):
        c = self.connection
        c.privmsg(self.channel, message)