from copy import copy
import re

import bank


def authorised_to_shup(source, owner):
    return source == owner

# Red team: Rob is Rosalina on the Phantom  &  Arvinda is Baby Luigi on the Blue Falcon
# News: Mario Kart result in! Rob and Arvinda beat Oliver and Ian
# potbot: 10 on arvinda
#  bowser: littlerob just transferred 1 to potbot

current_pot = None
mario_name = 'littlerob'


def what_to_say(bot, source, request, private):
    global current_pot
    if request.startswith("potbot: "):
        return messaged_directly(bot, source, request[len("potbot: "):], private)
    if source == mario_name and request == 'News: Mario Kart match starting!':
        messages = []
        if current_pot:
            current_pot.distribute_equally()
            messages.append("That went badly. Distributing previous bets to original owners.")

        current_pot = pot("Red team will win")
        messages.append(str(current_pot))
        return messages
    if source == mario_name and 'team is the best!' in request and current_pot:
        if request == 'Red team is the best!':
            winners = current_pot.distribute('for')
        elif request == 'Blue team is the best!':
            winners = current_pot.distribute('against')
        else:
            return []
        current_pot = None
        if winners:
            return [
                u'Winners were: {}'
                .format(', '.join(["{} {}".format(*winner) for winner in winners.iteritems()]))
            ]

    return []


def messaged_directly(bot, source, request, private):
    global current_pot
    if request == 'pug me':
        return ['http://i.imgur.com/Q4m8Drf.jpg']
    match = re.match('.*?(\d{1,3}).*?on (red|blue)$', request)
    if match:
        if not current_pot:
            return ['{}: There is currently nothing to bet on.'.format(source)]
        amount = float(match.groups(0)[0])
        if bank.get_current_balance(source) >= amount:
            bank.take_money({source: amount})
            if match.groups(0)[1] == 'red':
                direction = 'for'
            elif match.groups(0)[1] == 'blue':
                direction = 'against'
            else:
                raise Exception("where is red or blue? {}".format(request))
            current_pot.make_bet(source, amount, direction)
            return [
                '{}: Current bets are {}:{} red to blue. You now have {} left in the bank.'
                .format(
                    source,
                    current_pot.pot_size('for'),
                    current_pot.pot_size('against'),
                    bank.get_current_balance(source)
                )
            ]
    return []


class pot(object):
    def __init__(self, name):
        self.name = name
        self.bets = {'for': {}, 'against': {}}
        self.seed = 1

    def distribute_equally(self):
        winners = {}
        for bet_list in self.bets.values():
            for player in bet_list:
                if player not in winners:
                    winners[player] = 0
                winners[player] += 1
        self.distribute(winners)
        return winners

    def distribute(self, direction):
        winners = self.bets[direction]
        winners = copy(winners)  # Don't mess up the originals yet (although it shouldn't matter any more)
        winnings_mulitplier = (
            # Total amount to be distributed
            (self.pot_size('for') + self.pot_size('against')) /
            # Divided by amounts provided by winners (potbot doesn't want a share)
            (self.pot_size(direction) - self.seed)
        )
        print "winnings: {} {} {}".format(self.pot_size('for'), self.pot_size('against'), winnings_mulitplier)
        for winner in winners:
            winners[winner] *= winnings_mulitplier
        bank.give_money(winners)
        return winners

    def pot_size(self, direction):
        pot = sum(self.bets[direction].values()) + self.seed
        return round(pot, 2)

    def make_bet(self, bettor, amount, direction):
        pot = self.bets[direction]
        if not bettor in pot:
            pot[bettor] = 0
        pot[bettor] += amount

    def __str__(self):
        return (
            "Current bets for the proposition '{}' are {} for and {} against."
            .format(self.name, self.pot_size('for'), self.pot_size('against'))
        )
