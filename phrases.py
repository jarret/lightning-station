import random

PHRASES = [
"Personal responsibility is the new counter-culture.",
"Play stupid games, win stupid prizes.",
"Not your keys, not your Bitcoin.",
"Strong hands, long-term thinking.",
"Keep calm and hodl on.",
"Ring, Ring, Ring, Ring, Ring, Ring, Ring, Banana Phone!",
"I'm having a hard time holding these alligators down. Woo!.",
"Don't buy Bitcoin. It's going to crash.",
"No one uses Bitcoin anymore, the blocks are full.",
"Vitalik Buterin is a blockchain genius.",
"Don't buy Bitcoin. It has no intrinsic value.",
"Don't buy Bitcoin. It is in a death spiral.",
"Don't buy Bitcoin. It is a passing fad.",
"Don't buy Bitcoin. It is not backed by anything.",
"Bitcoin is legacy technology.",
"Bitcoin is a ponzi scheme.",
"No such thing as a free lunch.",
]


def get_phrase():
    return random.choice(PHRASES)
