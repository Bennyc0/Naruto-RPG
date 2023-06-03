import time
import random
from multiprocessing import Process
import os

# Itteration 1, scuffed*

class entity:
    # If your confused about the declaring of constructor, it's just setup to have a default, exclucding
    def __init__(self, username, level = 100, health = random.randint(5,10), attack = random.randint(1,3), defence = random.randint(1,3), skill = ["Punch"]):
        self.username = username
        # Levels are calculated by dividing the value by a 100, 1 level per 100 exp ->
        self.level = level
        self.health = health
        self.attack = attack
        self.defence = defence
        self.skill = skill
        
    def __str__(self):
        # If you try to print the object the following string is returned ->
        return f"\n{self.name}: Level {int(self.level / 100)}, Health {self.health}, Attack {self.attack}, Defence {self.defence},"

    def levelUp(self, exp):
        if self.level / 100 != self.level + exp:
            time.sleep(1)
            print("level Up! ", self.level / 100 + 1)
            self.health += random.randint(1,2)
            self.attack += random.randint(1,2)
            self.defence += random.randint(1,2)

        self.level += exp
    
    def damage(self, defender):
        print("Attack")
        defender.health -= 1
        # defender.health =- self.attack - defender.defence + 1
        print(f"{defender.name} is at {defender.health} health!")

def fight(entity1, entity2):
    # Requires more testing, runs player and enemy attacks at the same time.
    while entity1.health > 0 or entity2.health > 0:
        if __name__ == '__main__':
            Process(target=entity1.damage, args=(entity2,)).start()
            Process(target=entity2.damage, args=(entity1,)).start()

# All Bosses
boss1 = entity("Itachi", 100, 10 , 2, 2, ["Punch", "FireBall"])
# Test
place_holder = entity("Player", 10, 2, 2, ["Punch"])
print(boss1)


