from re import match as regex_match
from os import path

my_folder = path.dirname(__file__)
filename = path.join(my_folder, '/sowpods_words/{}.txt')


def authorised_to_shup(source, owner):
    return owner

# game over hubot: You have no remaining guesses
# game over hubot: Congratulations, you still had
# make a move hubot: The x letter word is: _ _ _ _ _ _ _
# oops lost a letter hubot: You already tried E so let's pretend that never happened, shall we?

current_game = None


def what_to_say(bot, source, request, private):
    global current_game
    if source != 'hubot':
        return []

    make_a_move = regex_match("The (?P<word_length>\w+) letter word is:", request)
    if make_a_move:
        word_length = int(make_a_move.group(1))
        if not current_game:
            current_game = HangmanGame(word_length)

        current_game.check_length(word_length)

        word_status = request.split(":")[1].split(' ')
        current_game.game_status(word_status)

        return ['hubot: hangman {}'.format(current_game.next_letter())]

    if "You have no remaining guesses" == request or request.startswith("Congratulations, you still had"):
        current_game = None
        return []

    lost_a_letter = regex_match(
        "You already tried (?P<letter>\w+) so let's pretend that never happened, shall we?",
        request
    )
    if lost_a_letter and current_game:
        current_game.add_played_letter(lost_a_letter.group(1).lower())
        return ['oops']

    return []


class HangmanGame(object):
    def __init__(self, word_length):
        self.word_length = word_length
        self.letters_tried = []
        self.word_status = ['_'] * word_length

    def check_length(self, word_length):
        if self.word_length != word_length:
            raise Exception(
                "I expected the current word to be {} but it's {} letters long"
                .format(self.word_length, word_length)
            )

    def add_played_letter(letter):
        self.letters_tried.append(letter)

    def game_status(word_status):
        if len(word_status) != self.word_length:
            raise Exception(
                "I expected the current word to be {} but word status {} implies it's {} letters long"
                .format(self.word_length, word_status, len(word_status))
            )
        for index, letter in enumerate(word_status):
            if self.word_status[index] not in [letter, '_']:
                raise Exception(
                    "I thought the word was {} but apparently it's now {}"
                    .format(" ".join(self.word_status), " ".join(word_status))
                )
            else:
                self.word_status[index] = letter

    def next_letter():
        next_letter = self.most_common_letter_words_matching_pattern("".join(self.word_status), self.letters_tried)
        print next_letter
        return next_letter[0]

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
        potential_words = find_words_matching_pattern(pattern, letters_tried)
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
        return max(word_counts_reversed), words_to_return
