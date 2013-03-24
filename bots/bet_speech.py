#! /usr/bin/env python

from random import uniform
from time import sleep
from urllib2 import urlopen
import bet_config
reload(bet_config)

def authorised_to_shup(source, owner):
    return True

def what_to_say(source, text, nickname, private):
    if text.find("Place your bets please!") >= 0 and source == bet_config.betmaster:
        alg_name = bet_config.betting_bot_map[nickname]
        my_bet = getattr(betting_algorithms, alg_name)(text)
        if my_bet != 'no bet':
            sleep(uniform(0,2))
            return ['%s: %s' % (bet_config.betmaster, my_bet)]
    return []

class BettingAlgorithms(object):
    def get_odds(self, text):
        odds = {}
        for index, team in enumerate(['red', 'blue', 'draw']):
           team_odds = text.split("0.")[index + 1].split(' ')[0]
           if len(team_odds) == 1:
              team_odds = team_odds + '0'
           team_odds.update({team:int(team_odds)})
        return odds
    
    def lowestodds(self, text):
        odds = self.get_odds(text)
        if odds['red'] < odds['blue']:
            return '%s on red' % ((odds['blue'] - odds['red']) * 4)
        elif odds['blue'] < odds['red']:
            return '%s on blue' % ((odds['red'] - odds['blue']) * 4)
        else:
            return 'no bet'
        
    def draw(self, text):
        odds = self.get_odds(text)
        if odds['draw'] < 10:
            return '20 on a draw'
    
    def red(self, text):
        odds = self.get_odds(text)
        if odds['red'] < 45:
            return '20 on red'
        
    def blue(self, text):
        odds = self.get_odds(text)
        if odds['blue'] < 45:
            return '20 on blue'
        
    def log_page(self):
        log_page = urllib2.urlopen('http://%s/lukelog.php' %
                                   bet_config.mario_stats_ip)
        log_page = log_page.read()
        log_page = [logline.split(',')
                        for logline in log_page.split('<br />')]
        
    def handicaps(self):
        handicaps = urllib2.urlopen('http://%s/robaverage.php' %
                                    bet_config.mario_stats_ip)
        handicaps = handicaps.read()
        handicaps = dict([logline.split(',')
                          for logline in handicaps.split('<br/>')][:-1])

    def underrated_long_term_average(self, text):
        log_page = self.log_page()
        handicaps = self.handicaps()
        valuations = {'blue':0, 'red':0}
        for player in log_page[1:5]:
            valuations[player[0]] += float(handicaps[player[1]])
        return self.underrated(valuations, 25)
    
    def underrated_my_estimates(self, text):
        log_page = self.log_page()
        valuations = {'blue':0, 'red':0}
        for player in log_page[1:5]:
            valuations[player[0]] += float(handicaps[player[1]])
        return self.underrated(valuations, 25)
    
    def underrated(self, valuations, enthusiasm):
        amount_to_bet = abs(int((valuations['blue'] -
                                 valuations['red']) * enthusiasm))
        if valuations['blue'] - valuations['red'] > 0.7:
            return "bowser: %s on blue" % amount_to_bet
        elif valuations['red'] - valuations['blue'] > 0.7:
            return "bowser: %s on red" % amount_to_bet

betting_algorithms = BettingAlgorithms()