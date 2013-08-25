from threading import Thread
from time import sleep
from random import choice, randint

commands = ['open the mailbox', 'read the leaflet', 'open the front door', 'bank', 'l', 'in', 'go in', 'i', 'read newspaper', 'throw newspaper at gate', 'offer lunch to spirits', 'shine lamp at gate', 'give lunch', 'give garlic', 'give book', 'ring bell', 'look', 'take all', 'ring bell', 'hit spirits with newspaper', 'd', 'enter gateway', 'ring bell', 'enter gateway', 'read book', 'i', 'n', 's', 'e', 'w', 'u', 'n', 'n', 'take all', 'jump', 'stand on pedestal', 'u', 'd', 'w', 'w', 'w', 'ne', 'take bar', 'e', 'e', 'shovel bat guano', 'take shovel', 'use shovel on guano', 'i', 'put garlic in sack', 'put lunch in sack', 'take shovel', 'put knife in sack', 'score', 'put book in sack', 'put wire in sack', 'put bottle in sack', 'put sack in sack', 'i', 'put bell in sack', 'look', 'drop newspaper', 's', 'nw', 'nw', 'nw', 'n', 's', 'e', 'w', 'sw', 's', 'read book', 's', 'daisy', 'u', 's,take all', 'e', 'i', 'e', 'tie rope around neck', 'nw', 'w', 'se', 's', 'e', 'e', 's', 'nw', 'dig', 'nw', 's', 'dig', 'u', 'dig', 'dig', 'ring bell', 's', 'ring bell', 'ring bell', 'dig', 'daisy', 'shout', 'u', 'e', 'shout', 'e', 'w', 'laugh', 'e', 'n', 'press buttons', 'n', 'save', 'put screwdriver in sack', 'press red button', 'put wrench in sack', 'take all', 'press brown button', 'press yellow button', 'press red button', 'press red button', 's', 's', 'turn bolt with wrench', 'w', 'e', 'e', 'e', 's', 'echo', 'dig', '\\o/', 'take bar', 'w', 'w', 'e', 'n', 'e', 'e', 'n', 'n', 's', 'e', 's', 'd', 's', 'e', 'e', 'w', 'n', 'w', 's', 's', 'n', 'd', 'w', 'n', 's', 'n', 'e', 'dig', 'take icicle', 'n', 'take trunk', 'save', 'drop all', 'take lamp', 'take trunk', 'open trunk', 'score', 's', 'sw', 's', 's', 'w', 'w', 'e', 'e', 'e', 'n', 'd', 'look', 'i', 's', 'light lamp', 'e', 'e', 'e', 'n', 'sw', 'n', 's', 'd', 'w', 'n', 'e', 's', 'sw', 'nw', 'u', 'ring bell', 'w', 'w', 'w', 'n', 'e', 'throw trunk at mirror', 'take trunk', 'take mirror', 'look at mirror', 'take piece', 'take mirror piece', 'n', 'n', 'w', 'w', 'e', 'score', 'n', 'n', 'ne', 'e', 'n', 'e', 'ne', 'w', 'e', 'take bar', 'n', 's', 'd', 's', '', 's', 's', 'd', 'w', 'dig', 'e', 'd', 'w', 's', 'e', 'e', 'e', 'w', 'd', 'w', 'n', 's', 'w', 'e', 'u', 'n', 'n', 'n', 'e', 's', 'd', 'u', 's', 'n', 'n', 'u', 'w', 'e', 'n', 'w', 'w', 'e', 'n', 'n', 's', 'w', 's', 'w', 'u', 'd', 'l', 'n', 'w', 'e', 's', 'n', '10 on blue', 'sw', 'e', 'd', 's', 'u', 'n', 'n', 'n', 'e', 'w', 's', 'e', 'e', 'w', 'n', '', 'w', 's', 'w', 'w', 'e', 'w', 'e', 'e', 'n', 'n', 'u', 'ne', 'd', 'e', 'take brick', 'take can', 'take candles', 'throw brick', 'throw brick at wall', 'd', 'l', 'e', 's', 'd', 'w', 's', 'look  at wall', 's', 'd', 'u', 'n', 'w', 'd', 'u', 'w', 'sw', 'se', 'nw', 'ne', 'n', 's', 'w', 'jumpo', 'jump', 'balance', 'l', 'score', 'ring bell', 'i', 's', 'w', 'w', 'n', 's', 'w', 'e', 'w', 'w', 'e', 's', 'w', 'n', 'd', 'd', 'jump', 'turn off lamp', 'score', 'eat score', 'eat mud', 'i', 'open trunk of jewels', 'u', 'u', 'put out candles', 'drop candles', 'e', 'w', 's', 's', 'light lamp', 'extinguish lamp', 'e', 'jump', 'restore', 'yes\\ryes', 'restore', 'yes\\r\\nyes\\r\\yes', 'restart', 'restart', 'restart', 'restore', 'l', 'bejewel!', '', 'l', 'take trunk', 'i', 'drop wrench', 'take trunk', 'drop book', 'put rope in sack', 'take trunk', 'tie rope round neck', 'drop glass', 'tie rope to glass bottle', 'drop glass b', 'tie knot', 'drop bottle', 'drop glass bottle', 'take trunk', '', '', '', '', '', '', 'i', 'drop rope', 'drop sack', 'take trunk', 'drop all', 'take trunk', 'take all', 'drop rope', 'take shovel', 'drop bottle', 'take trunk', 'take shovel', 'l', 'n', 'take pump', 'use ump', 'pump pump', 'use pump', 'pump stuff', 'score', 'verbose', 'brief', 'superbrief', 'diagnostic', 'superverbose', 'verbose', 'i', 'rape garlic', 'kill self with sword', 'break shovel with lamp', 'tie lunch to trunk', 'open trunk', 'examine trunk', 'examine garlic', 'examine coil', 'examine knife', 'examine lamp', 'examine self', 'dig', 'l', 'n', 'examine pump', 'take trident', 'drop jewels', 'drop trunk', 'drop trunk', 'take trident', 'examine trident', 'attack groun with trident', 'kill self with trident', 'where the hell are we', 'teleport', 'dbg', 'poke garlic with trident', 'i', 'l', 'w', '', 's', 'poke trunk with trident', 'n', 'se', 'n', 'u', 'n', 'n', 'sw', 'n', 's', 'n', 'sw', 'e', 'w', 'w', 'examine wall', 'poke wall with trident', 'n', 'ne', 'poke theif with trident', 'give thief jewels', 'poke thief with trident', 'give sack to thief', 'give wire to thier', 'kill thief with trident', 'give chest of jewels to thief', 'i', 'w', 's', 'e', 'give wire to thief', 'w', 'e', 'n', 's', 's', 'e', 'd', 'take trunk', 'se', 'throw trunk at pump', 'take pump', 'take trunk', 's', 'take all', 'throw sack', 'jump', 'restore', 'restart', 'restore', 'look', 'i', 'take all', 'n', 'n', 'take all', 'drop wrench', 'take trident', 'drop bell', 'take trident', 'drop shovel', 'take trident', 'look', 'u', 'n', 'd', 'n', 'n', 'sw', 'e', 'e', 'd', 'poke bell with trident', 'u', 'n', 'poke mirror with trident', 'w', 'poke mirror with sack', 'poke wall with sack', 'poke sack with sack', 'poke sack with trident', 'w', 'd', 'e', 'e', 'n', 'n', 'n', 'n', 'n', 'w', 's', 's', 's', 'u', 'drop everything', 'u', 'take all', 'take all', 'look', 'n', 'e', 'e', 'e', 'n', 'd', 'e', 'e', 'ne', 'echo', 'bank', 'no echo', 'book', 'mai', 'hello', 'trains', 'mai', 'zork', 'trains to zork', '', 'TRAINS TO ZORK', 'wub', 'book', 'bank', 'bank', 'book', 'hello!', 'unbook', 'bank', '3 more', 'book', 'test', 'mario 1 more', 'u', 'shout', 'spam!', '3 more', 'hello', 'DAISY', 'hello', 'hello', 'How are you?', 'what is zork?', 'who am i?', 'what is zork?', 'take bar', 'drop all', 'i', 'take all', 'error', 'your mother', 'your mother', 'rwge', 'whut', 'test2', 'worth a try', '10 on red', 'e', 'w', 'e', 's', 'w', 's', 'd', 's', 'e', 'i', 'help', 'look', 'inventory', 'take the clove of garlic and shove it up your <message truncated>', 'go south', 'i know, make a hole in it', 'n', 'n', 'u', 'w', 'u', 's', 'w', 'u', 'e', 'take brick', 'score', 'throw brick at wall', 'take brick', 'take candles', 'throw brick at candles', 'take candles', 'l', 'w', 'look at inscription', 'your lamp is stupid', 'e', 'throw brick at entrance', 'look', 'w', 'w', 'w', 'w', 'read newspaper', 'n', 'n', 'd', 'd', 'w', 'n', 'n', 'n', 'e', 'u', 'u', 'hit thief with knife', 'hit thief with knife', 'i', 'score', 'look', 'e', 'e', 'w', 's', 'd', 's', 'e', 'e', 'n', 'e', 'ne', 'w', 's', 'w', 'nw', 's', 'd', 'w', 'e', 'sw', 'u', 's', 's', 'sw', 'se', 'e', 'a well', 'e', 'put necklace in sack', 'take necklace', 'w', 'e', 'e', 'read etchings', 'move bucket', 'w', 'w', 'd', 'read engravings', 'se', 'd', 'n', 'n', 'w', 's', 'w', 's', 's', 'n', 'd', 'e', 'w', 's', 'w', 'u', 'take knife', 'i', 'drop book', 'take keys', 'take coins', 'drop wire', 'take coins', 'take knife', 'drop bottle', 'take coins', 'drop bottle', 'drop sack', 'take coins', 'sw', 'e', 's', 'se', 'e', 's', 'n', 's', 'n', 'ne', 'odysseus', 'n', 'e', 'open trophy case', 'put coins in trophy case', 'nw', 'e', 'extinguish lamp', 'extinguish candles', 'e', 'e', 'move leaves', 'open grating', 'open grating with key', 'i', 'open grating with skeleton keys', 'use skeleton keys to open grating', 'take skeleton keys', 'take keys', 'unlock grating', 'unlock grating with keys', 'score', 'catch a plane', 'look', 'eat leaves', 'throw leaves at ob', 'are you alive?', 'l', 'turn lamp off', 'I', 'open grating with skeleton keys', 'open grating with shovel', 'keys', 'open grating with keys', 'unlock grating with keys', 'unlock grating with crowbar', 'leaves', 'leave them', 'move leaves', 'l', 'take leaves', 'poke leaves with trident', 'work out a bit', 'push ups', 'squat', 'eat leaves', 'l', 'w', 'w', 's', 'w', 'e', 'unlock door with key', 'i', 's', 's', 'n', 'n', 'e', 'open window', 'in', 'n', 'n', 'w', 'put necklace in trophy case', 'look', 'read lettering', 'put coins in trophy case', 'i', 'score', 'put necklace in trophy case', 'save', 'diagnose', 'inflict slightly-less-than-serious wound on self', 'put keys in trophy case', 'i', 'put candles in trophy case', 'kill self with sword', 'd', 'open trapdoor', 'down', 'lamp on', 'light lamp', 'turn on', 'e', 's', 's', 'w', 'score', 'i', 'n', 'n', 'n', 'e', 'e', 'e', 'restart', 'i', 'restart', 'w', 'z', 'zork', 'drop all', 'take all', 'turn off lamp', 'throw leaves at lamp', 'turn off lamp', 'restart', 'throw trident at sword', 'take stick', 'restart', 'restore', 'hit mailbox', 'l', 'hit necklace', 'hit coins', '', 'hit trap door', 'i', 'hit rope', 'hit keys', 'drink candles', 'eat keys', 'i', 'swallow sword', 'cut rope', 'hit rope with sword', 'juggle sword', 'cut rope with sword', 'amputate leg', 'l', 'sit on sofa', 'l', 'read lettering', 'i', 'w', 'light candle', 'light lamp', 's', 'w', 'take knife', 'e', 'w', 'n', 'n', 'n', 'n', 'n', 'restart', 'restart', 'restart', 'restore']

def authorised_to_shup(source, owner):
    if owner:
        return True
    else:
        return False

class BadExplorerThread(Thread):
    def __init__(self, bot):
        self.bot = bot
        self.alive = True
        Thread.__init__(self)

    def run(self):
        while self.alive:
            self.bot.message(self.bot.channel, ["zork: {}".format(choice(commands))])
            sleep(randint(60, 180))

monitor_threads = []

def what_to_say(bot, source, request, private):
    if request.find(bot.nickname) == 0:
        request = request[len(bot.nickname) + 1:].strip()
        if source == bot.owner:
            if request == 'start':
                monitor_threads.append(BadExplorerThread(bot))
                monitor_threads[-1].daemon = True
                monitor_threads[-1].start()
            elif request == 'stop':
                if len(monitor_threads) > 0:
                    monitor_threads[-1].alive = False
                    del monitor_threads[-1]
    return []
