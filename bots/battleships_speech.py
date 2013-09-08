import battleships_shared
from battleships_shared import boat_lengths, coords_to_internal, coords_to_printable, PositionedBoat, grid_size, direction_map, human_direction_map

reload(battleships_shared)

def authorised_to_shup(source, owner):
    return source == owner


def what_to_say(bot, source, text, private):
    if text.startswith('{}:'.format(bot.nickname)):
        request = text[len(bot.nickname) + 1:].strip()
        return battleships_bot.request_for_me(bot, source, request, private)
    elif private:
        return battleships_bot.request_for_me(bot, source, text, private)
    elif battleships_bot.valid_coord(text):
        return battleships_bot.might_be_a_move(bot, source, text, private)
    return []


class BattleshipsBot(object):
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.valid_row_letters = [chr(65 + index)
                                  for index in range(self.grid_size)]
        self.valid_column_numbers = [str(index + 1)
                                     for index in range(self.grid_size)]
        self.active_games = []
        self.not_playing = "{source}: I'm sorry to have to be the one to tell you this, but you aren't playing."

    def request_for_me(self, bot, source, text, private):
        self.bot = bot
        if text.startswith('challenge'):
            return self.challenge(source, text[len('challenge'):].strip())
        elif text in ['accept', 'cancel', 'forfeit', 'help',
                      'current games', 'my moves', 'status', 'show grids']:
            use_function = getattr(self, text.replace(' ', '_'))
            return use_function(source, self.bot.nickname)
        elif self.valid_coord(text):
            return self.make_move(source, text)
        elif self.valid_position_declaration(text):
            return self.set_position(source, text)
        return ["{}: I don't know what that is.".format(source)]

    def valid_coord(self, text):
        return len(text) == 2 and \
               text[0].upper() in self.valid_row_letters and \
               text[1] in self.valid_column_numbers

    def might_be_a_move(self, bot, source, text, private):
        try_move = self.make_move(source, text)
        if len(try_move) == 0:
            return try_move
        elif "game hasn't started yet" in try_move[0] or "you aren't playing" in try_move[0]:
            return []
        else:
            return try_move

    def challenge(self, source, target):
        if source == target:
            return ["{}: Don't be silly.".format(source)]
        for game in self.active_games:
            if source in game.players:
                if game.status == 'challenge':
                    return ["{}: You're already in a game! Forfeit it if you must".format(source)]
                else:
                    return ["{}: You already have an open challenge. "
                            "Cancel it if you want to start a new one.".format(source)]
            if target in game.players:
                if game.status == 'challenge':
                    return ["{source}: Sorry, {target} is already in a game. You need to wait." \
                            .format(source=source, target=target)]
                else:
                    return ["{source}: Sorry, {target} has already been challenged. "
                            "Ask them to cancel it so they can play with you. Or wait." \
                            .format(source=source, target=target)]
        self.active_games.append(BattleshipsGame((source, target),
                                                 self.bot,
                                                 self.grid_size,
                                                 self.valid_row_letters,
                                                 self.valid_column_numbers))
        return ['{source} has challenged {target}! Waiting for accept...'
                .format(source=source, target=target)]

    def cancel(self, source, nickname):
        index, game = self.find_my_game(source)
        if not game:
            return ["{source}: uh, I can't find anything to cancel"
                    .format(source=source)]

        if game.status in ['challenge', 'waiting for positions']:
            del self.active_games[index]
            self.bot.public([
                "{} has cancelled a game."
                .format(source)
            ])
            return []
        else:
            return ["{}: Too late to cancel that game. See it through or forfeit.".format(source)]

    def find_my_game(self, player_name):
        for index, game in enumerate(self.active_games):
            if player_name in game.players:
                return index, game
        return False, False

    def forfeit(self, source, nickname):
        index, game = self.find_my_game(source)
        if not game:
            return ["{source}: uh, I can't find anything to forfeit"
                    .format(source=source)]
        if game.status in ['playing']:
            forfeit_beneficiary = game.players[(game.players.index(source) + 1) % 2]
            del self.active_games[index]
            self.bot.public(
                ["{} has forfeited a game."
                 .format(source),
                 "{} wins!".format(forfeit_beneficiary)]
            )
            return []
        else:
            return self.cancel(source, nickname)

    def accept(self, source, nickname):
        _, game = self.find_my_game(source)
        if not game:
            return ["{source}: I'm sorry to have to be the one to tell you this, but no one has challenged you yet."
                    .format(source=source)]
        if game.players[0] == source:
            return ["{source}: You are the challenger. Only {player} can accept.".format(source=source, player=game.players[1])]
        if game.status == 'challenge':
            game.status = 'waiting for positions'
            self.bot.public(
                ["{}: {} has accepted! Both please PM me your boat positions."
                .format(*game.players)]
            )
            return []
        else:
            return ["{}: You're already playing"]

    def current_games(self, source, nickname):
        return [game.info() for game in self.active_games]

    def my_moves(self, source, nickname):
        for game in self.active_games:
            if source in game.players:
                if game.status == 'playing':
                    return game.print_moves(source)
                else:
                    return ["{}: Uh, the game hasn't started yet".format(source)]
        return [self.not_playing.format(source=source)]

    def make_move(self, source, text):
        for game in self.active_games:
            if source in game.players:
                if game.status == 'playing':
                    return game.make_move(source, text)
                else:
                    return ["{}: Uh, the game hasn't started yet".format(source)]
        return [self.not_playing.format(source=source)]

    def valid_position_declaration(self, text):
        args = text.split(' ')
        return (len(args) == 3 and
                args[0] in ['carrier', 'battleship', 'submarine', 'destroyer', 'patrol'] and
                args[1][0].upper() in self.valid_row_letters and
                args[1][1] in self.valid_column_numbers and
                args[2].upper() in ['V', 'H'])

    def set_position(self, source, text):
        for game in self.active_games:
            if source in game.players:
                if game.status == 'waiting for positions':
                    return game.set_position(source, text)
                elif game.status == 'challenge':
                    return ["{}: Uh, the game hasn't started yet".format(source)]
                else:
                    return ["{}: It's too late for that now. We're already playing."
                            .format(source)]
        return [self.not_playing.format(source=source)]

    def status(self, source, nickname):
        index, game = self.find_my_game(source)
        if not game:
            return ["{}: You're not in a game.".format(source)]
        if game.status == 'challenge':
            return ["{} has challenged {}.".format(*game.players)]
        elif game.status == 'waiting for positions':
            boats_left_count = [len(game.boats_to_be_positioned[player_number])
                                for player_number in range(2)]
            if min(boats_left_count) > 0:
                return ["Waiting for boats to be positioned. "
                        "Both {} and {} still need to place boats."
                        .format(*game.players)]
            elif boats_left_count[0] == 0:
                return ["Waiting for boats to be positioned. "
                        "{} still needs to place boats."
                        .format(game.players[1])]
            else:
                return ["Waiting for boats to be positioned. "
                        "{} still needs to place boats."
                        .format(game.players[0])]
        elif game.status == 'playing':
            return [
                "{player0} is playing {player1}. "
                "There have been {turns} turns. "
                "{player0} still has to sink {player0left} boats and "
                "{player1} has {player1left}. It is {nextperson}'s turn"
                .format(player0=game.players[0],
                        player1=game.players[1],
                        turns=max([len(move_set) for move_set in game.moves]),
                        player0left=game.boats_left_to_sink[0],
                        player1left=game.boats_left_to_sink[1],
                        nextperson=game.players[game.whose_turn])
            ]
        else:
            print game.status
            print source
            raise Exception("what is the game status")

    def show_grids(self, source, nickname):
        # All boats shown on source's grid using - and |
        # Successful enemy hits shown with x
        # On enemy grid squares that been hit are shown as x
        # Misses are shown with 0
        sources_grid = [['.' for _ in range(self.grid_size)]
                             for _ in range(self.grid_size)]
        index, game = self.find_my_game(source)
        if not game:
            return ["{}: You're not in a game.".format(source)]
        source_player_number = game.players.index(source)
        other_player_number = (source_player_number + 1) % 2
        other_player = game.players[other_player_number]

        for boat_type, boat in game.boats[source_player_number].iteritems():
            direction_to_draw = {(1, 0): '-', (0, 1): '|'}[boat.direction]
            for coord in boat.coords:
                if coord in boat.coords_left_to_hit:
                    sources_grid[coord[1]][coord[0]] = direction_to_draw
                else:
                    sources_grid[coord[1]][coord[0]] = 'x'
        messages = ["Your boats:"]
        messages.extend(self.ascii_grid(sources_grid))
        messages.append(" ")

        messages.append("{}'s boats:".format(other_player))
        enemy_grid = [['.' for _ in range(self.grid_size)]
                           for _ in range(self.grid_size)]
        for coord in game.moves[source_player_number]:
            if coord in game.hits[source_player_number]:
                    enemy_grid[coord[1]][coord[0]] = 'x'
            else:
                enemy_grid[coord[1]][coord[0]] = 'o'
        messages.extend(self.ascii_grid(enemy_grid))
        self.bot.message(source, messages)
        return []

    def ascii_grid(self, a_grid):
        messages = [" ".join(["."] +
                    [str(value) for value in range(1, self.grid_size + 1)])]
        for index, row in enumerate(a_grid):
            messages.append(" ".join([chr(65 + index)] + row))
        return messages

    def help(self, source, nickname):
        help_text = '''Battleships!
Say {nickname}: challenge <nickname> to challenge someone to a game of battleships!
Your challenge will stay open forever, or until you or the challenged person cancels
Say {nickname}: accept to start the game
Say {nickname}: cancel to cancel a game; you cannot do this once both players have placed their pieces
{nickname}: forfeit to lose the game
When the game starts, {nickname} will ask both players to PM and place their ships.
They must position carrier (5), battleship (4), submarine (3), destroyer (3), patrol (2)
They do so like: "carrier B3 H" or "destroyer A8 V"
A-{row_limit} is the row number, 1-{column_limit} is the column number. You state the location of the top left corner of the boat.
H or V is whether the boat is oriented in a row or column.
After both players have positioned, they alternate turns saying "B5", "E2", etc
Say {nickname}: my moves to see where you have already played in this game.
{nickname}: status to get the details of your current game
{nickname}: show grids to see where you boats are placed and what has been hit'''\
            .format(nickname=nickname,
                    row_limit=chr(64 + self.grid_size),
                    column_limit=self.grid_size)
        return help_text.split('\n')


battleships_bot = BattleshipsBot(grid_size)


class BattleshipsGame(object):
    def __init__(self,
                 players,
                 bot,
                 grid_size,
                 valid_row_letters,
                 valid_column_numbers):
        self.players = players
        self.bot = bot
        self.grid_size = grid_size

        # later this will be 'waiting for positions' or 'playing'
        # need the messages to tell people what's going on
        self.status = 'challenge'
        self.info_messages = {'challenge': '{} has challenged {}.',
                              'waiting for positions': '{} and {} are about to start a game.',
                              'playing': '{} and {} are in a game.'}
        self.whose_turn = 1
        self.boats = [{}, {}]
        self.boats_to_be_positioned = [
            ['carrier', 'battleship', 'submarine', 'destroyer', 'patrol']
            for _ in range(2)
        ]
        self.moves = [set(), set()]
        self.hits = [set(), set()]
        self.boats_left_to_sink = [5, 5]

    def info(self):
        return self.info_messages[self.status].format(*self.players)

    def next_player(self):
        self.whose_turn = (self.whose_turn + 1) % 2

    def make_move(self, source, text):
        if self.players.index(source) != self.whose_turn:
            return ["{}: It's not your turn yet!".format(source)]
        coords_this_move = coords_to_internal(text)
        self.next_player()
        if coords_this_move in self.moves[self.players.index(source)]:
            return ["{}: You already attacked that square! I guess you don't want a turn.".format(source)]
        self.moves[self.players.index(source)].add(coords_this_move)
        for boat_type, boat in self.boats[self.whose_turn].iteritems():
            status = boat.attack(coords_this_move)
            if status == "dead":
                self.hits[self.players.index(source)].add(coords_this_move)
                messages = ["{}: You sunk {}'s {}.".format(source, self.players[self.whose_turn], boat.boat_type)]
                self.boats_left_to_sink[self.players.index(source)] -= 1
                if self.boats_left_to_sink[self.players.index(source)] == 0:
                    messages.append("{}: That was {}'s last boat. You win!"
                                    .format(source, self.players[self.whose_turn]))
                    index, game = battleships_bot.find_my_game(source)
                    if not game:
                        raise Exception("Uh, how is {} not in a game?".format(source))
                    del battleships_bot.active_games[index]
                self.bot.public(messages)
                return []
            elif status == "hit":
                self.hits[self.players.index(source)].add(coords_this_move)
                return ["{}: You hit {}'s {}.".format(source, self.players[self.whose_turn], boat.boat_type)]
        else:
            return ["{}: You didn't hit anything.".format(source)]

    def print_moves(self, source):
        moves = [coords_to_printable(coord) for coord in self.moves[self.players.index(source)]]
        moves.sort()
        if len(moves) == 0:
            return []
        return ["{}: Your moves so far are: {}"
                .format(source, ', '.join(moves))]

    def set_position(self, source, text):
        new_boat_type, raw_location, raw_direction = text.split(' ')
        start_coords = coords_to_internal(raw_location)
        direction = direction_map[raw_direction.upper()]
        new_boat = PositionedBoat(new_boat_type, start_coords, direction)
        player_number = self.players.index(source)
        if new_boat.off_edge_of_board(self.grid_size):
            return ["That doesn't fit there! It goes off the edge of the board."]

        boat_list = self.boats[player_number]
        for boat_type, boat in boat_list.iteritems():
            if new_boat.overlaps(boat):
                return ["That overlaps with another boat you already placed: ",
                        "The {boat_type} at {coord} {direction}. You can move that boat if you want."
                        .format(boat_type=boat.boat_type,
                                coord=coords_to_printable(boat.location),
                                direction=human_direction_map[boat.direction])]
        boat_list[new_boat_type] = new_boat
        messages = []
        if new_boat_type in self.boats_to_be_positioned[player_number]:
            self.boats_to_be_positioned[player_number].remove(new_boat_type)
        else:
            messages.append("That one has already been placed but I'll let you move it.")
        messages.append("Boat positioned.")
        if len(self.boats_to_be_positioned[player_number]) == 0:
            messages.append("All your boats have been placed. Game will start when your opponent has done the same.")
            if len(self.boats_to_be_positioned[(player_number + 1) % 2]) == 0:
                self.status = 'playing'
                self.bot.public(
                    ["Game is starting between {} and {}"
                    .format(*self.players)]
                )
        return messages
