#! /usr/bin/env python

from random import uniform
from time import sleep

from config import betting_bot_map, betmaster
reload(config)

def what_to_say(source, text, nickname):
    if text.find("Place your bets please!") >= 0 and source == betmaster:
        my_bet = which_algorithm[nickname]
        if my_bet != 'no bet':
            sleep(uniform(0,2))
            retun ['%s: %s' % (betmaster, my_bet)]
    return []

def lowestodds(text):
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

which_algorithm = {'lowestodds':lowestodds}
