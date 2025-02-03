from game_data import MONSTER_DATA
from random import randint


class Monster:
    def __init__(self, name, level):
        self.name, self.level = name, level

        self.element = MONSTER_DATA[name]["stats"]["element"]
        self.base_stats = MONSTER_DATA[name]["stats"]
        self.health = self.base_stats["max_health"] * self.level
        self.health -= randint(0, 200)
        self.health = max(0, self.health)

        self.energy = self.base_stats["max_energy"] * self.level
        self.energy -= randint(0, 100)
        self.energy = max(0, self.energy)

        self.abilities = MONSTER_DATA[name]["abilities"]

        # xp
        self.xp = randint(0, 1000)
        self.level_up = self.level * 150

    def get_stat(self, stat):
        return self.base_stats[stat] * self.level

    def get_stats(self):
        return {
            "health": self.get_stat("max_health"),
            "energy": self.get_stat("max_energy"),
            "attack": self.get_stat("attack"),
            "defense": self.get_stat("defense"),
            "speed": self.get_stat("speed"),
            "recovery": self.get_stat("recovery"),
        }

    def get_abilities(self):
        return [ability for lvl, ability in self.abilities.items() if self.level > lvl]
