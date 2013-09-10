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
    if source == battleships_bot:
        return battleships_player.request_from_battleships(bot, text)
    elif text.startswith('{}:'.format(bot.nickname)):
        request = text[len(bot.nickname) + 1:].strip()
    elif private:
        request = text
    else:
        return []

    if request == 'random boats':
        return [", ".join(generate_random_boat_positions(grid_size))]
    elif request == "it's your turn" and source == bot.owner:
        if hasattr(battleships_player, "current_game"):
            battleships_player.current_game.make_move()
            return ["Sorry; wasn't paying attention"]
        else:
            return ["{}: I don't think I'm in a game...".format(source)]
    elif request == 'show your grid':
        if hasattr(battleships_player, "current_game"):
            return battleships_player.current_game.show_moves()
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

    def request_from_battleships(self, bot, text):
        challenge = regex_match('(?P<challenger>\w+) has challenged {}! Waiting for accept...'.format(bot.nickname), text)
        if challenge:
            self.current_game = BattleshipsGame(
                challenge.group('challenger'),
                self.grid_size
            )
            bot.public(["{}: accept".format(battleships_bot)])
            sleep(3)
            bot.message(battleships_bot, generate_random_boat_positions(self.grid_size))
            return ["\o/"]

        if hasattr(self, "current_game"):
            opponent = self.current_game.opponent
            # Responses that imply opponent made a move or it's my turn
            move_texts = [
                "Game is starting between {} and {}".format(opponent, bot.nickname),
                "{}: You already attacked that square! I guess you don't want a turn.".format(opponent),
                "{}: You sunk {}'s".format(opponent, bot.nickname),
                "{}: You hit {}'s".format(opponent, bot.nickname),
                "{}: You didn't hit anything.".format(opponent)
            ]
            for move_text in move_texts:
                if text.startswith(move_text):
                    return self.current_game.make_move()

            hit = regex_match("{}: You hit {}'s (?P<boat_name>\w+).".format(bot.nickname, opponent), text)
            if hit:
                self.current_game.last_move_was_hit(hit.group('boat_name'))

            sink = regex_match("{}: You sunk {}'s (?P<boat_name>\w+).".format(bot.nickname, opponent), text)
            if sink:
                self.current_game.last_move_was_sink(sink.group('boat_name'))

            if text == "{}: You didn't hit anything.".format(bot.nickname):
                self.current_game.last_move_was_miss()

            # This shouldn't come up (unless perhaps the battleships bot crashes?).
            if text == "{}: You're not in a game.".format(bot.nickname):
                del self.current_game
                return ["Oh. :("]
        return []


class BattleshipsGame(object):
    def __init__(self, opponent, grid_size):
        self.opponent = opponent
        self.grid_size = grid_size
        self.smallest_boat_left = 2
        self.opponent_grid = [["haven't tried" for _ in xrange(grid_size)] for _ in xrange(grid_size)]
        self.positions_attacked = []
        self.boats = {boat_name: [] for boat_name in boat_lengths}
        self.start_position = (randint(0, 8), randint(0, 8))

    def translate(self, value):
        if value == "haven't tried":
            return '-'
        elif value == "nothing":
            return 'o'
        elif value == "boat":
            return 'x'
        else:
            raise Exception("This grid makes no sense: {}".format(value))

    def show_moves(self):
        return [" ".join([self.translate(self.opponent_grid[column][row])
                          for column in xrange(self.grid_size)])
                for row in xrange(self.grid_size)]

    def make_move(self):
        for boat in self.boats:
            if len(self.boats[boat]) > 0:
                print "trying to hit the {}".format(boat)
                return self.circle_boat(boat)
        else:
            print "haven't found a boat yet"
            return self.make_searching_move()

    def make_searching_move(self):
        attack_positions = self.find_positions_not_checked()
        attack_positions_with_distances = [
            (distance_between_coords(position, self.start_position),
             position)
            for position in attack_positions
        ]
        attack_positions_with_distances.sort()
        position_to_attack = attack_positions_with_distances[0][1]
        self.positions_attacked.append(position_to_attack)
        return [coords_to_printable(position_to_attack)]

    def last_move_was_hit(self, boat):
        last_coord_attacked = self.positions_attacked[-1]
        set_coord(self.opponent_grid, last_coord_attacked, "boat")
        self.boats[boat].append(last_coord_attacked)

    def last_move_was_sink(self, boat):
        last_coord_attacked = self.positions_attacked[-1]
        set_coord(self.opponent_grid, last_coord_attacked, "boat")
        del self.boats[boat]
        self.smallest_boat_left = min([boat_lengths[boat] for boat in self.boats])

    def last_move_was_miss(self):
        last_coord_attacked = self.positions_attacked[-1]
        set_coord(self.opponent_grid, last_coord_attacked, "nothing")

    def find_positions_not_checked(self):
        unattacked = [(horiz, vert)
                      for vert in xrange(self.grid_size)
                      for horiz in xrange(self.grid_size)
                      if self.opponent_grid[horiz][vert] == "haven't tried"]
        unattacked_with_parity = [(coord, get_parity(coord, self.smallest_boat_left)) for coord in unattacked]
        parities = [parity for (coord, parity) in unattacked_with_parity]
        parity_counts = [(parities.count(parity), parity) for parity in xrange(self.smallest_boat_left)]
        best_parity = min(parity_counts)[1]
        return [coord for (coord, parity) in unattacked_with_parity if parity == best_parity]

    def circle_boat(self, boat):
        boat_coords = self.boats[boat]
        if len(boat_coords) == 0:
            raise Exception("Why are we trying to hit a boat we haven't found yet")
        elif len(boat_coords) == 1:
            for direction in ['up', 'down', 'left', 'right']:
                coord_try = get_adjacent(boat_coords[0], direction)
                if safe_get_coord(self.opponent_grid, coord_try) == "haven't tried":
                    self.positions_attacked.append(coord_try)
                    return [coords_to_printable(coord_try)]
        elif len(boat_coords) > 1:
            if boat_coords[0][0] == boat_coords[1][0]:
                # The coords are the same in the horizontal direction
                varying_direction = 1
            else:
                varying_direction = 0
            coords_hit = [boat[varying_direction] for boat in boat_coords]
            coords_hit.sort()
            value_constant_direction = boat_coords[0][(varying_direction + 1) % 2]

            coords_to_try = [
                [coords_hit[0] - 1, value_constant_direction],
                [coords_hit[-1] + 1, value_constant_direction]
            ]

            if varying_direction == 1:
                for coord in coords_to_try:
                    coord.reverse()

            for coord_try in coords_to_try:
                if safe_get_coord(self.opponent_grid, coord_try) == "haven't tried":
                    self.positions_attacked.append(coord_try)
                    return [coords_to_printable(coord_try)]
            else:
                raise Exception(
                    "I checked both ends of the boat and I already tried both of them {} {}"
                    .format(boat_coords, self.opponent_grid)
                )


def safe_get_coord(grid, coord):
    if max(coord) > len(grid) or min(coord) < 0:
        return "invalid"
    else:
        try:
            return grid[coord[0]][coord[1]]
        except:
            return Exception(
                "I checked the grid size but still had a problem. grid: {}, coord: {}"
                .format(grid, coord)
            )


def set_coord(grid, coord, value):
    grid[coord[0]][coord[1]] = value


def get_parity(coord, divisor):
    return (coord[0] + coord[1]) % divisor


def get_adjacent(coords, direction):
    print coords
    direction_map = {'up': (0, -1),
                     'down': (0, 1),
                     'left': (-1, 0),
                     'right': (1, 0)}[direction]
    return (coords[0] + direction_map[0], coords[1] + direction_map[1])


def distance_between_coords(coord1, coord2):
    return sum([(coord1[i] - coord2[i])**2 for i in xrange(2)])**0.5


battleships_bot = 'ships'
battleships_player = BattleshipsPlayer(grid_size)
