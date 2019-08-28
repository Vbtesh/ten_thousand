import numpy as np
import random
from .util import split
from .util import prob_1
from .util import prob_15
from time import sleep
from fractions import Fraction

class Dice:
    def __init__(self):
        self.value = 0
        
    def roll(self):
        self.value = random.randint(1, 6)

class Ten_k:
    def __init__(self, players_names):
        self.num_p = len(players_names)
        self.scores = [0 for i in range(self.num_p)]
        self.dices = [Dice() for i in range(6)]
        self.turn = random.randint(1, self.num_p)
        self.turn_passed = {}
        self.players = {}
        for i in range(1, self.num_p + 1):
            self.turn_passed[i] = 0
            self.players[i] = players_names[i - 1]
        
        print("+++++ Welcome to 10 000! +++++")
        print("Players for this game are:")
        for num, player in self.players.items():
            print(num, ":", player)
        print("")
            
    def print_state(self):
        print("")
        print("Players' scores:")
        for num, score in zip(range(1, self.num_p + 1), self.scores):
            print(self.players[num], ":", score)
        print("It's {x}'s turn to play.".format(x = self.players[self.turn]))
        print("")
    
    def next_turn(self):
        self.turn_passed[self.turn] += 1
        next_turn = self.turn_passed[self.turn]
        self.turn += 1
        if self.turn > self.num_p:
            self.turn = 1
        return next_turn
        
    def roll_dices(self, num_dices, name):
        # Initialize number of dices and roll dices
        dices = self.dices[:num_dices]
        rolls = []
        valid = {}
        #print(len(dices))
        for dice, idx in zip(dices, range(1, len(dices) + 1)):
            dice.roll()
            rolls.append(dice.value)
            if dice.value == 1 or dice.value == 5:
                valid[idx] = dice.value
        # Construct print statement
        upper = ""
        middle = ""
        lower = ""
        d_num = ""
        for i, j in zip(rolls, range(1, len(rolls) + 1)):
            upper += "+---+ "
            middle += "| {a} | ".format(a = i)
            lower += "+---+ "
            d_num += " #{a}   ".format(a = j)
        # Print results        
        print("{x} rolled:".format(x = name))
        print(upper)
        print(middle)
        print(lower)
        print(d_num)
        return rolls, valid
    
    def evaluate(self, rolls, ones = False, fives = False):            
        # Count 1s and 5s
        num_1 = 0
        num_5 = 0
        for i in rolls:
            if i == 1:
                num_1 += 1
            elif i == 5:
                num_5 += 1
        # Evaluation
        score = 0
        # Fail 
        if num_1 == 0 and num_5 == 0:
            return 0, False, False
        # Gains for ones
        if not ones:
            if num_1 > 2:
                score += 1000 * (num_1 - 2)
                ones = True
            else :
                score += 100 * num_1
        else:
            score += 1000 * num_1
            if num_1 == 0:
                ones = False
        # Gains for fives
        if not fives:
            if num_5 > 2:
                score += 700 * (num_5 - 2)
                fives = True
            else:
                score += 50 * num_5
        else:
            score += 700 * num_5
            if num_5 == 0:
                fives = False 
        return score, ones, fives 
    
    def take_turn(self, name, dices, score = 0, ones = False, fives = False, bot = False):
        num_dices = len(dices)
        rolls, valid = self.roll_dices(num_dices, name)
        print("")
        print("Valid dices are: ", valid)
        print("")
        nested_score, inter_ones, inter_fives = self.evaluate(rolls, ones, fives)
        #print(score, ones, fives)
        sleep(2)
        if nested_score == 0:
            print("Sorry... Good luck next time.")
            score = 0
            return score
        else:
            print("This roll is worth {a}.".format(a = nested_score))
            print("")
            if not bot:
                while True:
                    choice = input("""Which dice(s) do you wish to keep? (Insert dice numbers using the following format => 532) Answer: """)
                    to_keep = []
                    # Prevent returning empty string
                    if choice == "":
                        print("Non valid choice, check dices or response format...")
                        continue
                    for i in choice:
                        try:
                            to_keep.append(valid[int(i)])
                        except KeyError:
                            print("Non valid choice, check dices or response format...")
                            break
                    if len(to_keep) == len(choice):
                        #print(to_keep, choice)
                        keep_string = ""
                        for i in choice:
                            keep_string += "[#" + i + ", " + str(valid[int(i)]) + "] "
                        print("OK! Keeping dices: {a}.".format(a = keep_string))
                        print("")
                        break
            else:
                choice, to_keep = bot.choose(score, nested_score, valid, "safe")
                keep_string = ""
                for i in choice:
                    keep_string += "[#" + str(i) + ", " + str(valid[int(i)]) + "] "
                print("OK! Keeping dices: {a}.".format(a = keep_string))
                print("")
                sleep(4)
            inter_score, ones, fives = self.evaluate(to_keep, ones, fives)
            score += inter_score
            dices = dices[:-len(to_keep)]
            if not dices:
                dices = [Dice() for i in range(6)]
            print("Current score for this turn is {a}".format(a = score))
            
            if not bot:
                forward = input("Continue ? Yes: [Enter] No: [n] Answer: ")
                if forward == "n":
                    #print(score)
                    return score
                else:
                    return self.take_turn(name, dices, score, ones, fives)
            else:
                fear = bot.fear(dices)
                if fear < 0.5:
                    print("Probability of success is {a}".format(a = fear))
                    print("Bot is scared, stopping...")
                    return score
                elif score >= 300:
                    print("Probability of success is {a}".format(a = fear))
                    print("Bot has reached its objective, stopping...")
                    return score
                else:
                    print("Probability of success is {a}".format(a = fear))
                    print("Let us go, continuing...")
                    return self.take_turn(name, dices, score, ones, fives, bot=bot) 

    def play(self):
        while True:
            self.print_state()
            name = self.players[self.turn]
            if name[:3] == "bot":
                bot = Robot(name, self.scores[self.turn - 1])
            else:
                bot = False
            print("----------------- {a}'s turn' -----------------".format(a = name))
            nested_score = self.take_turn(name, self.dices, bot=bot)
            #print(nested_score)
            hypo_score = self.scores[self.turn - 1] + nested_score
            if hypo_score == 10000:
                self.print_state()
                print("----------------- End of game -----------------")
                print("{a} takes the victory! The game is over.".format(a= name))
                break
            elif hypo_score > 10000:
                print("{a} is too much! {b}'s current score is {c}, he/she needs {d} to reach 10K...".format(a = nested_score,
                                                                                                             b = name, 
                                                                                                             c = self.scores[self.turn - 1],
                                                                                                             d = 10000-self.scores[self.turn - 1]))
                print("----------------- End of turn' -----------------")
            else:
                self.scores[self.turn - 1] += nested_score
                print("{a}'s total score after turn {b} is {c}, he/she gained {d}.".format(a = name, 
                                                                                           b = self.turn_passed[self.turn], 
                                                                                           c = self.scores[self.turn - 1],
                                                                                           d = nested_score))
                print("----------------- End of turn' -----------------")
            # Pass to next player
            self.turn_passed[self.turn] += 1
            self.turn = self.turn + 1
            if self.turn > self.num_p:
                self.turn = 1
            sleep(2)  
    
class Robot:
    def __init__(self, name, score = 0):
        self.name = name
        self.score = score
        
    def choose(self, score, rolls_value, valid, strategy=None):
        goal = 10000 - self.score
        print("{a}'s score is {b}, the goal is {c}".format(a = self.name, b = self.score, c = goal))
        if strategy == "safe":
            print("Playing safe")
            available = rolls_value + score
            if available >= 300 and available <= goal:
                return [k for k in valid.keys()], [v for v in valid.values()]
            elif available < 300:
                best = 6
                for dice, value in valid.items():
                    if value < best:
                        best = value
                        choice = [dice]
                        to_keep = [value]
                return choice, to_keep
            
    def fear(self, dices):
        return prob_15(len(dices))