from officialanswers import officical_answers
import recommender
import argparse
import math
from matplotlib import pyplot as plt
from scipy import stats
import pickle


class Bot:
    def __init__(self, smart=True):
        self.officical_answers = officical_answers
        self.remaining_words = len(self.officical_answers)
        self.smart = smart

        self.information_bits_axis = []
        self.actual_guesses_axis = []

    def reset(self):
        self.officical_answers = officical_answers
        self.remaining_words = len(self.officical_answers)

        self.information_bits_axis.clear()
        self.actual_guesses_axis.clear()

    def filter(self, guess, result):
        self.officical_answers = [word for word in self.officical_answers if recommender.viable_word(guess, result, word)]
        self.remaining_words = len(self.officical_answers)

    def play_game(self):
        round = 1
        helper = recommender.Recommender(self.smart)

        print("Welcome to Wordle!")
        print("Round 1")
        print("The top 5 first recommended guesses are: LEAST, SLATE, TRAIL, TRACE, and TRAIN.")
        while True:
            guess = input("Enter your guess: ")
            result = input("Enter the result: ")

            if result == "GGGGG":
                print("You win!")
                return
            
            print('-' * 20)
            round += 1

            helper.filter(guess, result)

            print("Round " + str(round))
            print("There are " + str(helper.remaining_words) + " remaining words.")
            guess_dict = helper.one_layer_guess_dict()

            print("The top 5 recommended guesses are: " + str(sorted(guess_dict.items(), key=lambda x: x[1])[:5]))



    def simulate_game(self, key):
        round = 1
        guess = "LEAST"
        helper = recommender.Recommender(self.smart)

        while True:
            self.information_bits_axis.append(math.log2(helper.remaining_words))

            print("Remaining words: " + str(helper.remaining_words))
            print("Round " + str(round) + ": guessing " + guess + "...")
            result = recommender.wordle_pattern(guess, key)
            print("Result: " + result)

            if result == "GGGGG":
                print("You win!")
                self.actual_guesses_axis = [i for i in range(round, 0, -1)]
                return
            
            helper.filter(guess, result)
            round += 1

            print('-' * 20)

            if (helper.remaining_words == 1):
                guess = helper.officical_answers[0]
            else:
                guess_dict = helper.one_layer_guess_dict()
            
                guess = min(guess_dict, key = guess_dict.get)


  
def collect_data(smart):
    bot = Bot(smart)
    # bot.play_game()
    total_x_axis = []
    total_y_axis = []

    x_axis_file = open("x-axis.txt", "wb")
    y_axis_file = open("y-axis.txt", "wb")

    for word in officical_answers:
        bot.simulate_game(word)
        total_x_axis += bot.information_bits_axis
        total_y_axis += bot.actual_guesses_axis

        bot.reset()

    pickle.dump(total_x_axis, x_axis_file)
    pickle.dump(total_y_axis, y_axis_file)

    plt.scatter(total_x_axis, total_y_axis)
    plt.xlabel("Information bits")
    plt.ylabel("Actual guesses")
    plt.show()

def fit_function():
    x_axis = pickle.load(open("x-axis.txt", "rb"))
    y_axis = pickle.load(open("y-axis.txt", "rb"))

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_axis, y_axis)
    fitted_line = list(map(lambda x: slope * x + intercept, x_axis))

    print(slope, intercept, r_value, p_value, std_err)

    plt.scatter(x_axis, y_axis)
    plt.plot(x_axis, fitted_line, 'r', label='fitted line')
    plt.xlabel("Information bits")
    plt.ylabel("Actual guesses")
    plt.show()


#print(viable_word("SPEED", "GBGYB", "STEAL"))

#NO-smart mode without considering whether guess is in word list : 3.6220302375809936
#No-smart mode considering : 3.540388768898488
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play Wordle')
    parser.add_argument('-s', '--smart', action=argparse.BooleanOptionalAction, help='smart mode')
    args = parser.parse_args()

    bot = Bot(args.smart)
    bot.play_game()
    # bot.filter("LEAST", "YBBBB")
    # bot.filter("COULD", "BBYGB")
    # bot.filter("FULLY", "BGBGG")
    # print(recommender.wordle_pattern("FULLY", "ALLOW"))
    # print(recommender.viable_word("ALLOW", "BYGBB", "FULLY"))
    
    # results = []
    # for word in officical_answers:
    #     bot.simulate_game(word)
    #     results.append(bot.actual_guesses_axis[0])
    #     bot.reset()
    
    # print("Average number of guesses: " + str(sum(results) / len(results)))

    # plt.hist(results, bins=range(1, 8))
    # plt.xlabel("Number of guesses")
    # plt.ylabel("Frequency")
    # plt.show()