#! /usr/bin/env python
# 
# srjbot
#
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

#def retrieve_gen(self):
#        try:
#           gen_log_page[0][0] = gen_log_page[0][0].lstrip('<font size="5">')
#            return gen_log_page
#        except AttributeError as err:
#            print 'Found error %s' % str(err)
#            return None
#        except urllib2.URLError as err:
#            print 'Error trying to open webpage! Returning None'
#            return None



import threading
import random
from datetime import date, datetime
import time
import urllib2, re

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

mario_stats_ip = '10.47.196.80'

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
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

    def check_and_answer(self, e, text):
        c = self.connection
        source = e.source.nick
        time.sleep(random.uniform(0,0.5))
        random_value = random.randint(0,100)
        if text.find("Place your bets please!") >= 0 and source == 'bowser':
            c.privmsg(self.channel, "bowser: %s on blue" % random_value)
        elif random_value < 8:
            c.privmsg(self.channel, "DAISY")

def main():
    import sys

    server = 'irc.rd.tandberg.com'
    port = 6667
    channel = '#mario'
    nickname = 'daisy'

    bot = TestBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()