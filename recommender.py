from officialanswers import officical_answers
from officialguesses import official_guesses
import math
import re

BASE_INFORMATION = math.log2(len(officical_answers))

#Already ran function fitting, constants are:
SLOPE = 0.2156798105668716
INTERCEPT = 1.3078756507624365
R_VALUE = 0.8277331865280964
P_VALUE = 0
STD_ERR = 0.0015963247138005457

def fitted_line(x):
    return SLOPE * x + INTERCEPT

def viable_word(guess_word, result, dict_word):
    """
    Returns a bool for whether the word is viable or not
    based on the guess and the resulting pattern
    """

    greens = [i.start() for i in re.finditer('G', result)]
    if greens:
        for i in greens:
            if guess_word[i] != dict_word[i]:
                return False
            dict_word = dict_word[:i] + '_' + dict_word[i + 1:]
            
    yellows = [i.start() for i in re.finditer('Y', result)]
    if yellows:
        for i in yellows:
            if guess_word[i] == dict_word[i]:
                return False
            if guess_word[i] not in dict_word:
                return False
            dict_word = dict_word.replace(guess_word[i], '_', 1)

    blacks = [i.start() for i in re.finditer('B', result)]
    if blacks:
        for i in blacks:
            if guess_word[i] in dict_word:
                return False
            
    return True

def wordle_pattern(guess, key):
    """
    Returns the wordle pattern for a given guess and key
    Example: wordle_pattern("LEAST", "WHIRL") -> "YBBBB"
    """
    pattern = ["B"]*5

    # Find greens
    for index, c in enumerate(guess):
        if key[index] == c:
            pattern[index] = "G"

            key = key[:index] + "_" + key[index + 1:]
            guess = guess[:index] + "-" + guess[index + 1:]

    # Find yellows
    for index, c in enumerate(guess):
        if c in key:
            pattern[index] = "Y"

            key = key.replace(c, "_", 1)
            guess = guess.replace(c, "_", 1)


    return "".join(pattern)

    

class Recommender:
    def __init__(self, smart=True):
        self.officical_answers = officical_answers
        self.guess_bank = officical_answers if smart else official_guesses
        self.smart = smart
        self.remaining_words = len(self.officical_answers)
        self.information_remaining = BASE_INFORMATION

    def reset(self):
        self.officical_answers = officical_answers
        self.guess_bank = officical_answers if self.smart else official_guesses
        self.remaining_words = len(self.officical_answers)
        self.information_remaining = BASE_INFORMATION

    def filter(self, guess, result):
        self.officical_answers = [word for word in self.officical_answers if viable_word(guess, result, word)]
        self.guess_bank = [word for word in self.guess_bank if viable_word(guess, result, word)]
        self.remaining_words = len(self.officical_answers)
        self.information_remaining = math.log2(self.remaining_words)

    def information(self, word):
        information_dict = {}
        self.remaining_words = len(self.officical_answers)

        for remaining_word in self.officical_answers:
            information_dict[wordle_pattern(word, remaining_word)] = information_dict.get(wordle_pattern(word, remaining_word), 0) + 1
        # x_axis = list(information_dict.keys())
        # y_axis = list(information_dict.values())

        # plt.bar(x_axis, y_axis)
        # plt.show()

        information = 0
        for key in information_dict:
            information -= (information_dict[key]/self.remaining_words) * math.log2(information_dict[key]/self.remaining_words)
        return information
    
    def two_layer_information(self, word):
        information = 0
        information_dict = {}
        self.remaining_words = len(self.officical_answers)

        for remaining_word in self.guess_bank:
            information_dict[wordle_pattern(word, remaining_word)] = information_dict.get(wordle_pattern(word, remaining_word), 0) + 1
            
        for key in information_dict:
            max_information = 0
            self.filter(word, key)
            for filtered_word in self.officical_answers:
                second_information = self.information(filtered_word)
                if second_information > max_information:
                    max_information = second_information
            self.reset()
            information += (information_dict[key]/self.remaining_words) * max_information
        return information + self.information(word)

    def one_layer_guess_dict(self):
        guess_dict = {}
        for word in self.guess_bank:
            #p is the probability of the word being the answer
            p = 1/self.remaining_words if word in self.officical_answers else 0
            guess_dict[word] = p + (1 - p) * (1 + fitted_line(self.information_remaining - self.information(word)))
            #guess_dict[word] = self.information(word)

        return guess_dict
    


if __name__ == "__main__":
    information_dict = {}
    test = Recommender()
    # for word in officical_answers:
    #     information_dict[word] = test.two_layer_information(word)
    #     print("Finished checking " + word + ", information: " + str(information_dict[word]))
    # print(dict(sorted(information_dict.items(), key=lambda item: item[1], reverse=True)[:20]))
    # test.filter("LEAST", "BYBBB")
    # test.filter("DRONE", "YBBGY")
    # for word in test.officical_answers:
    #     information_dict[word] = test.information(word)
    #     print("Finished checking " + word + ", information: " + str(information_dict[word]))
    # print(dict(sorted(information_dict.items(), key=lambda item: item[1], reverse=True)[:20]))
    print(viable_word("GOODY", "BGBBG", "HOBBY"))
