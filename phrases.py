import random

PHRASES = [
"Personal responsibility is the new counter-culture.",
"Play stupid games, win stupid prizes.",
"Not your keys, not your Bitcoin.",
"Strong hands, long-term thinking.",
"Keep calm and hodl on.",
"Ring, Ring, Ring, Ring, Ring, Ring, Ring, Banana Phone!",
"I'm having a hard time holding these alligators down.",
"Don't buy Bitcoin. It's going to crash.",
"No one uses Bitcoin anymore, the blocks are full.",
"Everyone knows that Vitalik Buterin is the smartest person.",
"Don't buy Bitcoin. It has no intrinsic value.",
"Don't buy Bitcoin. It is in a death spiral.",
"Don't buy Bitcoin. It is a passing fad.",
"Don't buy Bitcoin. It is not backed by anything.",
"Bitcoin is legacy technology.",
"Bitcoin is a ponzi scheme.",
"No such thing as a free lunch.",
"Don't make me run. I'm full of chocolate.",
"If you meet the Buddah on the road, kill him.",
"Words have no meaning.",
"Cypherpunks write code.",
"A spectre is haunting the world, the spectre of crypto-anarchy.",
"Your beard is weird.",
"We are all Satoshi except for Craig Wright",
"1 BTC Is Worth 1 BTC.",
"\"Running bitcoin\" -@halfin, Jan 10, 2009",
"Bitcoin Twitter is the best e-sports team.",
"The longest chain is whichever one Pieter Wuille is on.",
"Buying Bitcoin will make you smart in the future.",
"r/buttcoin on suicide watch",
"It's certainly possible I was bamboozled.",
"The Proof-of-Work speaks for itself.",
]


def get_phrase():
    return random.choice(PHRASES)
