from copy import copy

boat_lengths = {
    'carrier': 5,
    'battleship': 4,
    'submarine': 3,
    'destroyer': 3,
    'patrol': 2
}

direction_map = {'H': (1, 0), 'V': (0, 1)}
human_direction_map = {(1, 0): 'H', (0, 1): 'V'}


class PositionedBoat(object):
    def __init__(self, boat_type, location, direction):
        self.boat_type = boat_type
        self.location = location
        self.direction = direction
        self.boat_length = boat_lengths[boat_type]
        self.coords = [tuple([location[i] + (direction[i] * index) for i in range(2)])
                       for index in range(self.boat_length)]
        self.coords_left_to_hit = copy(self.coords)

    def off_edge_of_board(self, grid_size):
        return max(self.coords[-1]) + 1 > grid_size

    def overlaps(self, boat):
        for coord in self.coords:
            if coord in boat.coords:
                return True
        else:
            return False

    def coord_hit(self, coord):
        return coord in self.coords_left_to_hit

    def attack(self, coord):
        if self.coord_hit(coord):
            self.coords_left_to_hit.remove(coord)
            if len(self.coords_left_to_hit) == 0:
                return "dead"
            else:
                return "hit"
        else:
            return "miss"


def coords_to_printable(coords_internal):
    return chr(65 + coords_internal[1]) + str(coords_internal[0] + 1)


def coords_to_internal(coords_human):
    return (ord(65 + coords_human[1]), int(coords_human[0]) - 1)


grid_size = 9