from re import match as regex_match
from os import path
from time import sleep

my_folder = path.dirname(__file__)
source_file = my_folder + '/sowpods_words/{}.txt'


def authorised_to_shup(source, owner):
    return owner

# game over hubot: You have no remaining guesses
# game over hubot: Congratulations, you still had
# make a move hubot: The x letter word is: _ _ _ _ _ _ _
# oops lost a letter hubot: You already tried E so let's pretend that never happened, shall we?
# is it a real word? hubot: The 9 letter word was: JIMHICKEY

current_game = None


def what_to_say(bot, source, request, private):
    if private:
        check_word = regex_match("is this a word: (?P<word>\w+)", request)
        if check_word:
            return ["Is {} a real word? {}"
                    .format(
                        check_word.group(1),
                        str(is_it_real_word(check_word.group(1)))
                    )]
    
    global current_game
    if source != 'hubot':
        return []

    make_a_move = regex_match("The (?P<word_length>\w+) letter word is:", request)
    if make_a_move:
        word_length = int(make_a_move.group(1))
        if not current_game:
            current_game = HangmanGame(word_length)

        current_game.check_length(word_length)

        word_status = request.split(":")[1].strip().split(' ')
        current_game.game_status(word_status)

        return [current_game.next_letter()]

    if "You have no remaining guesses" == request or request.startswith("Congratulations, you still had"):
        current_game = None
        bot.messenger.messenger.wipe(bot.channel)
        return []

    someone_lost_a_letter = regex_match(
        "You already tried (?P<letter>\w+) so let's pretend that never happened, shall we?",
        request
    )
    if someone_lost_a_letter and current_game:
        i_lost_a_letter = current_game.add_played_letter(someone_lost_a_letter.group(1).lower())
        if i_lost_a_letter:
            return ['oops']

    big_reveal = regex_match(
        "The (?P<length>\w+) letter word was: (?P<word>\w+)",
        request
    )
    if big_reveal:
        word = big_reveal.group(2).lower()
        print [word]
        if is_it_real_word(word):
            return []
        else:
            return [
                "hubot: {} is not in SOWPODS; There's no way I could have guessed that"
                .format(word.upper())
            ]

    return []


def is_it_real_word(word_to_check):
    source = open(source_file.format(len(word_to_check)))
    words = [word.strip() for word in source.readlines()]
    return word_to_check in words


class HangmanGame(object):
    def __init__(self, word_length):
        self.word_length = word_length
        self.letters_tried = []
        self.word_status = ['_'] * word_length
        self.game_alive = True

    def check_length(self, word_length):
        if self.word_length != word_length:
            raise Exception(
                "I expected the current word to be {} but it's {} letters long"
                .format(self.word_length, word_length)
            )

    def add_played_letter(self, letter):
        if len(letter) == 1 and letter not in self.letters_tried:
            self.letters_tried.append(letter)
            return True
        else:
            return False

    def game_status(self, word_status):
        if len(word_status) != self.word_length:
            raise Exception(
                "I expected the current word to be {} but word status {} implies it's {} letters long"
                .format(self.word_length, word_status, len(word_status))
            )
        for index, letter in enumerate(word_status):
            if self.word_status[index] not in [letter.lower(), '_']:
                raise Exception(
                    "I thought the word was {} but apparently it's now {}"
                    .format(" ".join(self.word_status), " ".join(word_status))
                )
            else:
                self.word_status[index] = letter.lower()
            if letter != '_':
                self.add_played_letter(letter.lower())

    def next_letter(self):
        if not self.game_alive:
            return []
        next_letter, words, frequency_of_second_best_letter = self.most_common_letter_words_matching_pattern("".join(self.word_status), self.letters_tried)
        if next_letter[0] == 0:
            self.game_alive = False
            sleep(1)
            return "I don't know any words that match that"
        elif next_letter[0] == 1 and frequency_of_second_best_letter == 0:
            self.game_alive = False
            return "hubot: hangman {}".format(words[0])
        self.add_played_letter(next_letter[1])
        sleep(1)
        return "hubot: hangman {}".format(next_letter[1])

    def find_words_matching_pattern(self, pattern, letters_tried):
        source = open(source_file.format(len(pattern)))
        words = [word.strip() for word in source.readlines()]
        for index, letter in enumerate(pattern):
            if letter == '_':
                words = [word for word in words if word[index] not in letters_tried]
            else:
                words = [word for word in words if word[index] == letter]
        return words

    def most_common_letter_words_matching_pattern(self, pattern, letters_tried):
        potential_words = self.find_words_matching_pattern(pattern, letters_tried)
        letters_to_try = [chr(letter_ordinal) for letter_ordinal in xrange(97, 123) if chr(letter_ordinal) not in letters_tried]
        word_lists = {letter: [] for letter in letters_to_try}
        for word in potential_words:
            for letter in letters_to_try:
                if letter in word:
                    word_lists[letter].append(word)
        word_counts_reversed = [(len(value), key) for key, value in word_lists.iteritems()]

        words_to_return = word_lists[max(word_counts_reversed)[1]]
        if len(words_to_return) > 30:
            words_to_return = len(words_to_return)

        word_counts_reversed.sort()
        return word_counts_reversed[-1], words_to_return, word_counts_reversed[-2][0]
