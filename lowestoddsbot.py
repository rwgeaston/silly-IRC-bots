#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from bettingbot import BettingBot

class LowestOddsBot(BettingBot):
    def bet(self, text):
        redodds = text.split("0.")[1].split(' ')[0]
        if len(redodds) == 1:
            redodds = redodds + '0'
        red = int(redodds)
        blueodds = text.split("0.")[2].split(' ')[0]
        if len(blueodds) == 1:
            blueodds = blueodds + '0'
        blue = int(blueodds)
        if red < blue:
            return '%s on red' % ((blue - red) * 4)
        elif blue < red:
            return '%s on blue' % ((red - blue) * 4)
        else:
            return 'no bet'