from random import shuffle
from copy import copy
from re import match as regex_match
from time import time

card_map = {
    1: 'Guard',
    2: 'Priest',
    3: 'Baron',
    4: 'Handmaid',
    5: 'Prince',
    6: 'King',
    7: 'Countess',
    8: 'Princess'
}

card_frequencies = [0, 5, 2, 2, 2, 2, 1, 1, 1]

bot_messenger = None
bot_channel = None
current_game = None
last_game_time = 0

def messenger(target, message):
    if target == "public message":
        bot_messenger(bot_channel, [message])
    else:
        bot_messenger(target, [message])

def label_card(card_value):
    return "{} - {}".format(card_value, card_map[card_value])

def authorised_to_shup(source, owner):
    return False

def what_to_say(bot, source, text, private):
    global bot_messenger
    global bot_channel
    global current_game
    global last_game_time
    bot_messenger = bot.message
    bot_channel = bot.channel
    if private:
        if 'wipe game' in text:
            current_game = None
    else:
        if text.startswith("{}: ".format(bot.nickname)):
            command = text[len("{}: ".format(bot.nickname)):]
            
            if command == 'help':
                return [
                    'Love Letter',
                    'Full rules here http://www.alderac.com/tempest/files/2012/09/Love_Letter_Rules_Final.pdf',
                    'Commands are: "First to [N]" to start a new game, "join", "start" when enough players have joined',
                    '"status" and "scores" to find out about the game in progress',
                    '"card values" to be reminded of the values of each card',
                    'When choosing which card to play or guess, just give the numeric value of that card']

            if command == 'card values':
                return [
                    'value - name (frequency): description',
                    '8 - Princess (1): Lose if discarded',
                    '7 - Countess (1): Must discard if caught with King or Prince',
                    '6 - King (1): Trade hands',
                    '5 - Prince (2): One player must discard their hand',
                    '4 - Handmaid (2): Protection until your next turn',
                    '3 - Baron (2): Compare hands; lower hand is out',
                    '2 - Priest (2): Look at a hand',
                    "1 - Guard (5): Guess a player's hand",
                ]
            new_game = regex_match("first to ([0-9]{1})", command)
            if new_game:
                if current_game:
                    return ["{}: There's already a game being played"
                            .format(source)]
                else:
                    current_game = LoveLetterGame(
                        messenger, 
                        int(new_game.groups(0)[0]),
                        source
                    )
            else:
                if not current_game:
                    return ["{}: Start a game with 'first to N'"
                            .format(source)]
                else:
                    if command == 'start':
                        if time() < last_game_time + 3600:
                            return ["You played already in the last hour."]
                        current_game.start_game(source)
                    elif command == 'join':
                        current_game.add_player(source)
                    elif current_game.game_started:
                        if command == 'status':
                            current_game.status()
                        elif command == 'scores':
                            current_game.show_scores()
                        elif command == 'next round':
                            current_game.new_round(source)
                        else:
                            outcome = current_game.make_move(source, command)
                            if outcome == 'game over':
                                current_game = None
    return []


class LoveLetterGame(object):
    def __init__(self, messenger, winning_score, starting_player):
        self.messenger = messenger
        self.players = [starting_player]
        self.game_started = False
        self.winning_score = min(int(winning_score), 5)
        self.messenger(
            "public message",
            "{} has started a game of Love Letter."
            .format(starting_player)
        )

    def add_player(self, name):
        if not self.game_started:
            if name not in self.players:
                self.players.append(name)
                self.messenger(
                    "public message",
                    "{} has joined the game. {} players at the moment."
                    .format(name, len(self.players))
                )
            else:
                self.messenger(
                    "public message",
                    "{}: You're already in the game.".format(name))
        if len(self.players) == 4:
            self.start_game(self.players[0])

    def start_game(self, source):
        if source == self.players[0] and not self.game_started:
            if len(self.players) < 2:
                self.messenger("public message", "Not enough players yet.")
                return
            self.game_started = True
            shuffle(self.players)
            self.scores = {player: 0 for player in self.players}
            self.messenger("public message", "Game is starting.")
            self.current_round = LoveLetterRound(self.messenger, self.players)

    def make_move(self, player, command):
        if not self.current_round:
            self.messenger(
                "public message",
                "{}: Please start another round with 'next round' command."
                .format(player)
            )
            return
        outcome = self.current_round.turn_decide_action(player, command)
        if outcome:
            print 'outcome of make a move: ', outcome
            self.current_round = None
            if outcome != "No one":
                self.scores[outcome] += 1
            inverse = [(value, key) for key, value in self.scores.items()]
            current_leader = max(inverse)[1]
            if  self.scores[current_leader] == self.winning_score:
                self.messenger(
                    "public message",
                    "Game is over. {} has won!".format(current_leader)
                )
                self.show_scores()
                return "game over"
            else:
                self.messenger(
                    "public message",
                    "{} is current leader with {} points. Winner is first to {}."
                    "Please start another round with 'next round' command."
                    .format(current_leader, self.scores[current_leader], self.winning_score)
                )
        else:
            return "still playing"

    def new_round(self, player):
        global last_game_time
        last_game_time = time()
        if self.current_round:
            self.messenger(
                "public message",
                "{}: You can't start a new round when the last one hasn't finished."
                .format(player)
            )
        else:
            self.messenger(
                "public message",
                "Next round started."
            )
            self.current_round = LoveLetterRound(self.messenger, self.players)
        return

    def status(self):
        if not self.current_round:
            status = "Not current in a round."
        else:
            status = self.current_round.status()
        self.messenger(
            "public message",
            status
        )

    def show_scores(self):
        scores = ", ".join(["{}: {}".format(player, self.scores[player]) 
                            for player in self.players])
        self.messenger(
            "public message",
            "Scores are {}".format(scores)
        )

class LoveLetterRound(object):
    def __init__(self, messenger, players):
        self.messenger = messenger
        self.players = copy(players)
        self.cards = []
        self.current_player = 0
        self.current_turn_state = 'play_turn'
        self.discarded_value = {player: 0 for player in self.players}
        for card, frequency in enumerate(card_frequencies):
            for instance in range(frequency):
                self.cards.append(card)

        shuffle(self.players)
        shuffle(self.cards)
        self.discarded_card = self.cards.pop()
        if len(self.players) == 2:
            face_up_discarded_cards = [self.cards.pop() for _ in range(3)]
            discarded_cards_string = ", ".join(
                [label_card(card) for card in face_up_discarded_cards]
            )
            self.messenger(
                "public message",
                "Face up (discarded) cards are {discarded}"
                .format(discarded=discarded_cards_string)
            )

        self.cards_held = {player: [self.cards.pop()] for player in self.players}
        self.protected = {player: False for player in self.players}
        for player in self.cards_held:
            self.messenger(
                player,
                "You are holding {}"
                .format(label_card(self.cards_held[player][0]))
            )
        self.start_next_turn()

    def start_next_turn(self):
        self.current_turn_state = 'play_turn'
        current_player = self.players[self.current_player]
        self.protected[current_player] = False
        self.messenger(
            "public message",
            "It is {player}'s turn."
            .format(player=current_player)
        )
        next_card = self.cards.pop()
        if len(self.cards) == 0:
            self.messenger(
                "public message",
                "{} just picked up the last card."
                .format(current_player)
            )

        self.messenger(
            current_player,
            "You picked up {} (currently holding {})"
            .format(
                label_card(next_card),
                label_card(self.cards_held[current_player][0])
            )
        )
        self.cards_held[current_player].append(next_card)

    def turn_decide_action(self, player, instruction):
        if player != self.players[self.current_player]:
            self.messenger(
                "public message",
                "{}: It's not your turn".format(player)
            )
            return

        if self.current_turn_state not in ['play_turn', 'guess']:
            if instruction not in self.players:
                self.messenger(
                    "public message",
                    "{}: {} is not playing or already got knocked out of this round"
                    .format(player, instruction)
                )
                return
            elif self.protected[instruction]:
                self.messenger(
                    "public message",
                    "{}: {} is protected by a handmaid. Try someone else."
                    .format(player, instruction)
                )
                return
            elif self.current_turn_state in ['king', 'baron'] and instruction == player:
                # cannot choose yourself
                self.messenger(
                    "public message",
                    "{}: You can't choose yourself for this card. Try someone else."
                    .format(player, instruction)
                )
                return
        return getattr(self, self.current_turn_state)(player, instruction)

    def play_turn(self, player, card):
        card = self.check_valid_card_number(player, card)
        if not card:
            return

        if card not in self.cards_held[player]:
            self.messenger(
                "public message",
                "{}: You don't have {}"
                .format(player, label_card(card))
            )
            return

        self.messenger(
            "public message",
            "{} played {}".format(player, label_card(card))
        )

        self.cards_held[player].remove(card)
        self.discarded_value[player] += card

        if card == 8:
            self.messenger(
                "public message",
                "{}: Why would you play the princess? You're out of the game."
                .format(player)
            )
            self.messenger(
                "public message",
                "{} is forced to discard their card {}"
                .format(player, label_card(self.cards_held[player].pop()))
            )
            self.remove_player()
            return self.next_turn()
        elif card == 7:
            return self.next_turn()
        elif card in [5, 6]:
            if 7 in self.cards_held[player]:
                self.messenger(
                    "public message",
                    "{}: You played the {} whilst holding the Countess (7). That's cheating!"
                    .format(player, label_card(card))
                )
                self.messenger(
                    "public message",
                    "{} is forced to discard their card {}"
                    .format(player, label_card(self.cards_held[player].pop()))
                )
                self.remove_player()
                return self.next_turn()
                return
            if card == 6:
                if self.any_other_unprotected_players(player):
                    self.messenger(
                        "public message",
                        "{}: Who do you want to trade with?"
                        .format(player)
                    )
                    self.current_turn_state = 'king'
                    return
                else:
                    self.messenger(
                        "public message",
                        "All other players are protected by a handmaid so doing nothing."
                    )
                    return self.next_turn()
            elif card == 5:
                self.messenger(
                    "public message",
                    "{}: Who do you want to force to discard?"
                    .format(player)
                )
                self.current_turn_state = 'prince'
                return
        elif card == 4:
            self.messenger(
                "public message",
                "{} is protected until their next turn"
                .format(player)
            )
            self.protected[player] = True
            return self.next_turn()

        elif card == 3:
            if self.any_other_unprotected_players(player):
                self.messenger(
                    "public message",
                    "{}: Who do you want to challenge?"
                    .format(player)
                )
                self.current_turn_state = 'baron'
            else:
                self.messenger(
                    "public message",
                    "All other players are protected by a handmaid so doing nothing."
                )
                return self.next_turn()
        elif card == 2:
            if self.any_other_unprotected_players(player):
                self.messenger(
                    "public message",
                    "{}: Whose card do you want to see?"
                    .format(player)
                )
                self.current_turn_state = 'priest'
            else:
                self.messenger(
                    "public message",
                    "All other players are protected by a handmaid so doing nothing."
                )
                return self.next_turn()
        elif card == 1:
            if self.any_other_unprotected_players(player):
                self.messenger(
                    "public message",
                    "{}: Whose card do you want to guess?"
                    .format(player)
                )
                self.current_turn_state = 'guard'
            else:
                self.messenger(
                    "public message",
                    "All other players are protected by a handmaid so doing nothing."
                )
                return self.next_turn()

    def king(self, player, trader):
        self.cards_held[player], self.cards_held[trader] = \
            self.cards_held[trader], self.cards_held[player]
        for person in [player, trader]:
            self.messenger(
                person,
                "You traded and are now holding {}"
                .format(label_card(self.cards_held[person][0]))
            )
        self.messenger(
            "public message",
            "{} and {} traded cards"
            .format(player, trader)
        )
        return self.next_turn()

    def prince(self, player, card_swapper):
        discard = self.cards_held[card_swapper].pop()
        self.messenger(
            "public message",
            "{} has been forced to discard {}."
            .format(card_swapper, label_card(discard))
        )
        if discard == 8:
            self.messenger(
                "public message",
                "{} is out after being forced to discard the Princess"
                .format(card_swapper)
            )
            self.remove_player(card_swapper)

        self.discarded_value[card_swapper] += discard
        if len(self.cards) > 0:
            new_card = self.cards.pop()
        else:
            new_card = self.discarded_card

        self.messenger(
            card_swapper,
            "{}: You picked up {}"
            .format(
                card_swapper,
                label_card(new_card))
        )
        self.cards_held[card_swapper].append(new_card)
        return self.next_turn()

    def baron(self, player, challengee):
        self.messenger(
            player,
            "{} has {}".format(challengee, label_card(self.cards_held[challengee][0]))
        )

        self.messenger(
            challengee,
            "{} has {}".format(player, label_card(self.cards_held[player][0]))
        )
        if self.cards_held[player][0] < self.cards_held[challengee][0]:
            self.messenger(
                "public message",
                "{} has the higher card! {} discards their {} and is out."
                .format(challengee, player, label_card(self.cards_held[player][0]))
            )
            self.remove_player()
            return self.next_turn()
        elif self.cards_held[player][0] > self.cards_held[challengee][0]:
            self.messenger(
                "public message",
                "{} has the higher card! {} discards their {} and is out."
                .format(player, challengee, label_card(self.cards_held[challengee][0]))
            )
            self.remove_player(challengee)
            return self.next_turn()
        else:
            self.messenger(
                "public message",
                "{} and {} have the same card. No one goes out."
                .format(player, challengee)
            )
            return self.next_turn()

    def priest(self, player, card_viewee):
        self.messenger(
            player,
            "{} has {}"
            .format(
                card_viewee,
                label_card(self.cards_held[card_viewee][0]))
        )
        self.messenger(
            "public message",
            "{} has seen {}'s card"
            .format(player, card_viewee)
        )
        return self.next_turn()

    def guard(self, player, guessee):
        self.current_turn_state = "guess"
        self.current_guess_victim = guessee
        self.messenger(
            "public message",
            "{}: what card do you want to guess {} has?"
            .format(player, guessee)
        )
        return

    def guess(self, player, card_guess):
        card_guess = self.check_valid_card_number(player, card_guess)

        if not card_guess:
            return

        if card_guess == 1:
            self.messenger(
                "public message",
                "{}: You're not allowed to guess 1 - Guard."
                .format(player)
            )
            return

        if card_guess == self.cards_held[self.current_guess_victim][0]:
            self.messenger(
                "public message",
                "{player} correctly guessed that {victim} has {card}. {victim} is out!"
                .format(
                    player=player,
                    victim=self.current_guess_victim,
                    card=label_card(self.cards_held[self.current_guess_victim].pop())
                )
            )
            self.remove_player(self.current_guess_victim)
        else:
            self.messenger(
                "public message",
                "{} incorrectly guessed that {} has {}."
                .format(
                    player,
                    self.current_guess_victim,
                    label_card(card_guess)
                )
            )
        return self.next_turn()

    def check_valid_card_number(self, player, card):
        try:
            card = int(card)
        except ValueError:
            self.messenger(
                "public message",
                "{}: I don't think {} is a number"
                .format(player, card)
            )
            return False
        try:
            label_card(card)
        except KeyError:
            self.messenger(
                "public message",
                "{}: I don't think {} is a valid card number"
                .format(player, card)
            )
            return False
        return card

    def remove_player(self, player=None):
        if not player:
            player = self.current_player
        if isinstance(player, basestring):
            player = self.players.index(player)
        self.players[player] = "player is out"
        return

    def next_turn(self):
        players_left = [player for player in self.players if player != "player is out"]
        if len(players_left) == 0:
            raise Exception("Where did everyone go?")
        elif len(players_left) == 1:
            self.messenger(
                "public message",
                "Everyone is out of the round except {player}! "
                "{player} wins this round! (They had {card})"
                .format(
                    player=players_left[0],
                    card=label_card(self.cards_held[players_left[0]][0])
                )
            )
            return players_left[0]

        if len(self.cards) == 0:
            self.messenger(
                "public message",
                "There are no cards left to pick up. "
                "Player with the highest card wins the round."
            )
            return self.find_round_winner()

        self.current_turn_state = "play_turn"
        self.current_player = (self.current_player + 1) % len(self.players)
        while self.players[self.current_player] == "player is out":
            self.current_player = (self.current_player + 1) % len(self.players)

        self.start_next_turn()

    def find_round_winner(self):
        highest_player = ["No one"]
        highest_value = 0

        for player in self.players:
            if player != "player is out":
                self.messenger(
                    "public message",
                    "{} is holding {}."
                    .format(player, label_card(self.cards_held[player][0]))
                )
                if self.cards_held[player][0] > highest_value:
                    highest_value = self.cards_held[player][0]
                    highest_player = [player]
                elif self.cards_held[player][0] == highest_value:
                    highest_player.append(player)

        if len(highest_player) == 1:
            self.messenger(
                "public message",
                "{} wins this round!".format(highest_player[0])
            )
            return highest_player[0]
        else:
            self.messenger(
                "public message",
                "{} and {} are holding the same card."
                .format(*highest_player))
            highest_player_discarded = ["No one"]
            highest_value = 0
            for player in highest_player:
                self.messenger(
                    "public message",
                    "{} has discarded {} worth of cards."
                    .format(player, self.discarded_value[player])
                )
                if self.discarded_value[player] == highest_value:
                    highest_player_discarded.append(player)
                elif self.discarded_value[player] > highest_value:
                    highest_player_discarded = [player]
                    highest_value = self.discarded_value[player]
            if len(highest_player_discarded) > 1:
                self.messenger(
                    "public message",
                    "I give up. No one wins this round."
                )
                return "No one"
            else:
                self.messenger(
                    "public message",
                    "{} wins!".format(highest_player_discarded[0])
                )
                return highest_player_discarded[0]

    def status(self):
        who = "It is {}'s turn. ".format(self.players[self.current_player])
        if self.current_turn_state == "play_turn":
            return (who + "Waiting for them to choose which card to play")
        elif self.current_turn_state == "guess":
            return (who + "Waiting for them to choose a card to guess that {} has."
                    .format(self.current_guess_victim))
        else:
            return (who + "They just played the {}. "
                    "Waiting for them to choose a player."
                    .format(self.current_turn_state))

    def any_other_unprotected_players(self, current_player):
        unprotected_players = {
            player for player, protected_state in self.protected.items() if not protected_state and player in self.players
        }
        if unprotected_players == {current_player}:
            return False
        else:
            return True
