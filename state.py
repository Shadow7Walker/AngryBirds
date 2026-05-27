import random

# Game State and variables
gameState = 0  # 0: input, 1: player1 turn, 2: player2 turn, 3: game over, -1: P1 bird, -2: P2 bird, -3: level, -4: wind, -5: setup
tim = 0
stk1 = 0.0
stk2 = 0.0
input = ""
text = "Enter Player_1 Name "
player1 = ""
player2 = ""
score1 = 0
score2 = 0
p = 0
bird1 = 0
bird2 = 0
wind = 0
windr = random.randrange(1, 5)
winner = 0
highScore = 0
scoreV = False
wait_for_mouse_release = False
stepCount = 0

# Shared resource pointers populated by main.py at runtime
screen = None
sounds = {}
step_callback = None
