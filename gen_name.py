import random
from names import FIRST_NAMES, LAST_NAMES


def gen_name():
    n = "%s %s" % (random.choice(FIRST_NAMES), random.choice(LAST_NAMES))
    return n.lower().title()

if __name__ == '__main__':
    print(gen_name())
