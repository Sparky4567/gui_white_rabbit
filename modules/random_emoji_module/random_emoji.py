from kaomoji.kaomoji import Kaomoji
import random

class Random_Emoji:
    def __init__(self):
        self.kao = Kaomoji()
        self.emoji_list = self.kao.categories[:-1]

    def pick_random(self):
        random_category = random.choice(self.emoji_list)
        res = self.kao.create(random_category)
        return res