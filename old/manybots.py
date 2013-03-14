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

from threading import Thread
import random
from datetime import date, datetime
import time
import urllib2, re

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

mario_stats_ip = '10.47.196.80'

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, number, server, port=6667):
        self.channel = channel
        self.number = number
        self.nickname = 'trinary%s' % number
        self.count = 0
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)],
                                            self.nickname, self.nickname)
        

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

    def check_and_answer(self, e, text):
        source = e.source.nick
        time.sleep(random.uniform(0,0.5))
        random_value = random.randint(0,100)
        if text.find("Place your bets please!") >= 0 and source == 'bowser':
            time.sleep(self.number + 1)
            remainder = self.number
            for iteration in range(self.count):
                remainder = remainder / 3
            remainder = remainder % 3
            if remainder == 0:
                self.message("Bowser: 999 on red")
            elif remainder == 1:
                self.message("Bowser: 999 on blue")
            else:
                self.message("Bowser: 999 on draw")
            self.count += 1
        elif text.find("%s just lost" % self.nickname) >= 0 and source == 'bowser':
            self.die('Rubbish; I lost my money')
                


class make_binary_bot(Thread):
    def __init__(self, *args):
        self.args = args
        Thread.__init__(self)
    def run(self):
        bot = TestBot(*args)
        bot.start()
    

def main():
    import sys

    server = 'irc.rd.tandberg.com'
    port = 6667
    channel = '#mario'

    for number in range(81):
        print number
        
        t = make_binary_bot(channel, number, server, port)
        #t = Thread(target = make_binary_bot, args=(channel, number, server, port))
        t.daemon = True
        t.start()
        time.sleep(10)

if __name__ == "__main__":
    main()
    while True:
        time.sleep(1)