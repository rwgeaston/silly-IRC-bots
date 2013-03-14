#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from random import uniform
from time import sleep
from generic_bot import TestBot

class BettingBot(TestBot):
    def check_and_answer(self, e, text):
        c = self.connection
        source = e.source.nick
        if text.find("Place your bets please!") >= 0 and source == 'bowser':
            my_bet = self.bet(text)
            sleep(uniform(0,2))
            self.message('bowser: %s' % my_bet)
