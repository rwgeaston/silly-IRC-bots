def authorised_to_shup(source, owner):
    if source == bot.owner:
        return True
    else:
        return False

def what_to_say(bot, source, text, private):
    if text.startswith('{}:'.format(nickname)):
        request = text[len(nickname) + 1:].strip()
        return battleships_bot.request_for_me(bot, source, request, private)
    elif private:
        return battleships_bot.request_for_me(bot, source, request, private)
    return []

class BattleshipsBot(object):
    def __init__(self):
        self.grid_size = 9
        self.valid_row_letters = [chr(65 + index)
                                  for index in range(self.grid_size)]
        self.valid_column_numbers = [str(index + 1)
                                     for index in range(self.grid_size)]
        self.active_games = []
        self.not_playing = "{source}: I'm sorry to have to be the one to tell you this, but you aren't playing."

    def request_for_me(self, bot, source, text, private):
        if text.startswith('challenge'):
            return self.challenge(source, text[len('challenge'):].strip())
        elif text in ['accept', 'cancel', 'forfeit', 'help', 'current games', 'my moves']:
            use_function = getattr(self, text.replace(' ', '_'))
            return use_function(source, nickname)
        elif len(text) == 2 and\
             text[0] in self.valid_row_letters and\
             text[1] in self.valid_column_numbers:
            return self.make_move(source, text)
        elif self.valid_position_declaration(text):
            return self.set_position(source, text)
        return ["{}: I don't know what that is.".format(source)]
    
    def challenge(self, source, target):
        for game in self.active_games:
            if source in game.players:
                if game.status == 'challenge':
                    return ["{}: You're already in a game! Forfeit it if you must".format(source)]
                else:
                    ["{}: You already have an open challenge. Cancel it if you want to start a new one.".format(source)]
            if target in game.players:
                if game.status == 'challenge':
                    return ["{source}: Sorry, {target} is already in a game. You need to wait."\
                            .format(source=source, target=target)]
                else:
                    return ["{source}: Sorry, {target} has already been challenged. Ask them to cancel it so they can play with you. Or wait."\
                            .format(source=source, target=target)]
        self.active_games.append(BattleshipsGame((source, target),
                                                 self.messenger,
                                                 self.grid_size,
                                                 self.valid_row_letters,
                                                 self.valid_column_numbers))
        return ['{source} has challenged {target}! Waiting for accept...'
                .format(source=source, target=target)]
    
    def cancel(self, source, nickname):
        for index, game in enumerate(self.active_games):
            if source in game.players:
                if game.status in ['challenge', 'waiting for positions']:
                    del self.active_games[index]
                    return ["{} has cancelled a game."
                            .format(source)]
                else:
                    ["{}: Too late to cancel that game. See it through"]
        return ["{source}: uh, I can't find anything to cancel"
                .format(source=source)]
    
    def forfeit(self, source, nickname):
        for index, game in enumerate(self.active_games):
            if source in game.players:
                if game.status in ['playing']:
                    players = game.players
                    for player in players:
                        if player != source:
                            forfeit_beneficiary = player
                            break
                    del self.active_games[index]
                    return ["{} has forfeited a game."
                            .format(source),
                            "{} wins!".format(forfeit_beneficiary)]
                else:
                    return self.cancel(source, nickname)
        return ["{source}: uh, I can't find anything to forfeit"
                .format(source=source)]
    
    def accept(self, source, nickname):
        for game in self.active_games:
            if source in game.players:
                if game.status == 'challenge':
                    game.status = 'waiting for positions'
                    return ["{} has accepted! Please PM me your boat positions."
                            .format(source)]
                else:
                    ["{}: You're already playing"]
        return ["{source}: I'm sorry to have to be the one to tell you this, but no one has challenged you yet."
                .format(source=source)]
    
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
                    return ["{}: It's too late for that now. We're already playing.".format(source)]
        return [self.not_playing.format(source=source)]
    
    def help(self, nickname):
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
Say {nickname}: my moves to see where you have already played in this game.'''\
            .format(nickname=nickname,
                    row_limit=chr(64 + self.grid_size),
                    column_limit=self.grid_size)
        return help_text.split('\n')

class BattleshipsGame(object):
    def __init__(self,
                 players,
                 messenger,
                 grid_size,
                 valid_row_letters,
                 valid_column_numbers):
        self.players = players
        self.messenger = messenger
        self.grid_size = grid_size
        
        # later this will be 'waiting for positions' or 'playing'
        # need the messages to tell people what's going on
        self.status = 'challenge'
        self.info_messages = {'challenge':'{} has challenged {}.',
                              'waiting for positions':'{} and {} are about to start a game.',
                              'playing':'{} and {} are in a game.'}
        self.direction_map = {'H':(1, 0), 'V':(0, 1)}
        self.human_direction_map = {(1, 0):'H', (0, 1):'V'}
        self.whose_turn = 1
        self.boats = [{}, {}]
        self.boats_to_be_positioned = [['carrier', 'battleship',
                                        'submarine', 'destroyer',
                                        'patrol']
                                       for index in range(2)]
        
    def info(self):
        return self.info_messages[self.status].format(*self.players)
    
    def next_player(self):
        self.whose_turn = (self.whose_turn + 1) % 2
    
    def make_move(self, source, text):
        # attack there
        pass
    
    def print_moves(self, source):
        # print the moves
        return ['print moves!']
    
    def coords_to_printable(self, coords_internal):
        return chr(65 + coords_internal[1]) + str(coords_internal[0])
    
    def coords_to_internal(self, coords_human):
        return (ord(65 + coords_human[1]), int(coords_human[0]))
    
    def set_position(self, source, text):
        boat_type, raw_location, raw_direction = text.split(' ')
        start_coords = self.coords_to_internal(raw_location)
        direction = self.direction_map[raw_direction]
        new_boat = positioned_boat(boat_type, start_coords, direction)
        player_number = self.players.index(source)
        boat_list = self.boats[player_number]
        if new_boat.off_edge_of_board(self.grid_size):
            return ["That doesn't fit there! It goes off the edge of the board."]
        for boat in boat_list:
            if new_boat.overlaps(boat):
                return ["That overlaps with another boat you already placed:",
                        "The {type} at {coord} {direction}"
                        .format(type=boat.boat_type,
                                coord=self.coords_to_printable(boat.location),
                                direction=self.human_direction_map[boat.direction])]
        boat_list.append(boat)
        messages = []
        if boat_type in self.boats_to_be_positioned[player_number]:
            self.boats_to_be_positioned[player_number].remove(boat_type)    
        else:
            messages.append("That one has already been placed but I'll let you move it.")
        messages.append("Boat positioned.", "Boats still to place are: {}"
                        .format(", ".join(self.boats_to_be_positioned)))
        if (len(self.boats_to_be_positioned[0]) == 0 and
            len(self.boats_to_be_positioned[1]) == 0):
            self.status = 'playing'
            self.messenger.add_to_queue()
        
class positioned_boat(object):
    def __init__(boat_type, location, direction):
        self.boat_type = boat_type
        self.location = location
        self.direction = direction
        self.boat_length = {'carrier':5, 'battleship':4,
                            'submarine':3, 'destroyer':3,
                            'patrol':2}[boat_type]
        self.coords = [tuple([start_coords[i] + (direction[i] * index) for i in range(2)])
                       for index in range(self.boat_length)]
        
    def off_edge_of_board(self, grid_size):
        return max(self.coords[-1]) + 1 > grid_size
        
    
battleships_bot = BattleshipsBot()