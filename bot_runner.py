from time import sleep
from threading import Thread

from planes import PlanesBot
from lowestoddsbot import LowestOddsBot

channel = '#cslounge-traaaaains'
server = 'irc.freenode.net'
owner = 'rwgeaston'

class run_bot(Thread):
    def __init__(self, *args):
        self.args = args
        Thread.__init__(self)
        
    def run(self):
        bot = self.args[0](*(self.args[1:]))
        bot.start()

bots = [[PlanesBot, 'planes'],
        #[LowestOddsBot, 'drybones']
        ]
        
bot_threads = []

for bot_class, nickname in bots:
    print bot_class, nickname
    bot_threads.append(run_bot(bot_class, channel, nickname, owner, server))
    print 'created'
    bot_threads[-1].daemon = True
    bot_threads[-1].start()
    sleep(5)

print 'everyone should be running'

while True:
    sleep(1)