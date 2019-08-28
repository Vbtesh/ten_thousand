from classes.resources import Ten_k, Robot, Dice 

players = input("Enter players' names separated by a ',': ")

players = [player.strip() for player in players.split(",")]

game = Ten_k(players)
game.play()