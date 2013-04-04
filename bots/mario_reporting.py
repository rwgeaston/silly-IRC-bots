from threading import Thread
from time import sleep
from urllib2 import urlopen

def capitalise(string):
    return string[:1].upper() + string[1:]

def authorised_to_shup(source, owner):
    if owner:
        return True
    else:
        return False

mario_website = '10.47.196.80'


class MonitorMarioSite(object):
    def __init__(self, bot, mario_ip):
        self.bot = bot
        self.mario_ip = mario_ip
        self.talk = True

        self.results = self.get_results()
        self.current_game = self.get_current_game()

    def update(self):
        new_results = self.get_results()
        if new_results != self.results:
            self.results = new_results
            self.message_results()

        new_game = self.get_current_game()
        if new_game != self.current_game:
            self.current_game = new_game
            self.message_current_game()

    def get_current_game(self):
        page = urlopen('http://{}/lukelog.php'.format(self.mario_ip)
        raw_content = page.read()[15:-13]
        lines = raw_content.split('<br />')
        game = {'timestamp':lines[0], 'Red':[], 'Blue':[]}
        for player in lines[1:]:
            colour, name, character, vehicle = player.split(',')
            game[capitalise(colour)].append((capitalise(name), character, vehicle))
        return game

    def get_results(self):
        page = urlopen('http://{}/robhandicaps.php'.format(self.mario_ip)
        raw_content = page.read()
        lines = raw_content.split('<br />')
        timestamp, result = lines[0].split(',')
        results = {'timestamp':timestamp,
                'result':result,
                'players':[]}
        for player in lines[1:]:
            name, handicap = player.split(',')
            results['players'].append((name, handicap))
        return results

    def message(self, messages):
        if self.talk:
            self.bot.message(self.channel, messages)

    def message_results(self):
        result_split = self.results['result'].split(' ')
        colour = result_split[0]
        players = [capitalise(player[:-1]) for player in result_split[2:]]

        players_and_handicaps = []
        for player in players:
            players_and_handicaps.extend([player, self.get_handicap(player)])
        messages = [
            'Mario kart results in! {} and {} beat {} and {}'.format(*players),
                    'New handicaps: {}: {}, {}: {}, {}: {}, {}: {}'.format(*players_and_handicaps),
                    '{} team is the best!'.format(colour)]
        self.message(messages)

    def get_handicap(self, player):
        for listing in self.results['handicaps']:
            if listing[0] == player:
                return listing[1]

    def message_current_game(self):
        messages = ['News: Mario Kart match starting!']
        blank_team_string = "{} team: {} is {} on the {} & {} is {} on the {}"
        for team in ['Red', 'Blue']:
            args = [team] + self.current_game[team][0] + self.current_game[team][1]
            messages.append(blank_team_string.format(*args))
        self.message(messages)

    def message_handicaps(self):
        messages = ["{} {}".format(*player) for player in self.results['players']]

class MonitorMarioSiteThread(Thread):
    def __init__(self, bot):
        self.bot = bot
        self.alive = True
        monitor = MonitorMarioSite(bot, mario_website)
        Thread.__init__(self)

    def run(self):
        while self.alive:
            monitor.update()
            sleep(30)

monitor_threads = []

def what_to_say(bot, source, request, private):
    if source == bot.owner:
        if request == 'start':
            monitor_thread.append(MonitorMarioSiteThread(bot))
            monitor_thread.daemon = True
            monitor_thread.start()
        elif request == 'stop':
            monitor_thread[0].alive = False
            del monitor_thread[0]
        elif request == 'test new':
            monitor_thread[0].monitor.message_current_game()
        elif request == 'test finished':
            monitor_thread[0].monitor.message_results()
    elif request == 'handicaps':
        monitor_thread[0].monitor.message_handicaps()
