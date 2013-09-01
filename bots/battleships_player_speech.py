from battleships_shared import boat_lengths, coords_to_internal, coords_to_printable, PositionedBoat, grid_size
from random import choice, randint


def authorised_to_shup(source, owner):
    return source == owner


def what_to_say(bot, source, text, private):
    if text.startswith('{}:'.format(bot.nickname)):
        request = text[len(bot.nickname):]
    elif private:
        request = text
    else:
        return []

    if request == 'random boats':
        return generate_random_boat_positions(grid_size)
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

    return ["{} {} {}".format(boat, placed_boats[boat].position, placed_boats[boat].direction) for boat in placed_boats]


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
    orientation = choice(('H', 'V'))
    coords = (randint(0, grid_size - 1), randint(0, grid_size - 1 - boat_lengths[boat]))
    if orientation == 'H':
        coords = (coords[1], coords[0])
    return PositionedBoat(boat, coords, orientation)
