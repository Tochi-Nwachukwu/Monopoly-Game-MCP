import random


def roll_dice():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)

    return {"dice1": d1, "dice2": d2}
