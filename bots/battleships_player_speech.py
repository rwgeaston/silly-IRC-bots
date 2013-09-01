import battleships_shared
from battleships_shared import boat_lengths, coords_to_internal, coords_to_printable, PositionedBoat, \
                               grid_size, direction_map, human_direction_map
from random import choice, randint
from re import match as regex_match
from time import sleep

reload(battleships_shared)


def authorised_to_shup(source, owner):
    return source == owner


def what_to_say(bot, source, text, private):
    if text.startswith('{}:'.format(bot.nickname)):
        request = text[len(bot.nickname) + 1:].strip()
    elif source == battleships_bot:
        return battleships_player.request_for_me(bot, text)
    elif private:
        request = text
    else:
        return []

    if request == 'random boats':
        return [", ".join(generate_random_boat_positions(grid_size))]
    else:
        return []


def generate_random_boat_positions(grid_size):
    placed_boats = {}
    for boat in boat_lengths:
        while True:
            new_boat_position = place_boat(boat, grid_size)
            if not overlaps(placed_boats, new_boat_position, grid_size):
                placed_boats.update({boat: new_boat_position})
                break

    return ["{} {} {}"
            .format(boat,
                    coords_to_printable(placed_boats[boat].location),
                    human_direction_map[placed_boats[boat].direction])
            for boat in placed_boats]


def overlaps(placed_boats, new_boat_position, grid_size):
    if new_boat_position.off_edge_of_board(grid_size):
        raise Exception("Why is this boat off the edge of the board? {} {} {}"
                        .format(new_boat_position.boat_type,
                                new_boat_position.location,
                                new_boat_position.direction))
    for boat in placed_boats:
        if new_boat_position.overlaps(placed_boats[boat]):
            return True
    return False


def place_boat(boat_type, grid_size):
    orientation = choice(((0, 1), (1, 0)))
    coords = (randint(0, grid_size - 1), randint(0, grid_size - 1 - boat_lengths[boat_type]))
    if orientation == (1, 0):
        coords = (coords[1], coords[0])
    return PositionedBoat(boat_type, coords, orientation)


class BattleshipsPlayer(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size

    def request_for_me(self, bot, text):
        challenge = regex_match('(?P<challenger>\w+) has challenged {}! Waiting for accept...'.format(bot.nickname), text)
        if challenge:
            self.current_game = BattleshipsGame(challenge.group('challenger'))
            bot.public(["{}: accept".format(battleships_bot)])
            sleep(3)
            bot.message(battleships_bot, generate_random_boat_positions(self.grid_size))
            return ["\o/"]
        else:
            return []


class BattleshipsGame(object):
    def __init__(self, opponent):
        self.opponent = opponent

battleships_bot = 'ships'
battleships_player = BattleshipsPlayer(grid_size)
