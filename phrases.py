import random

PHRASES = [
"Personal responsibility is the new counter-culture.",
"Play stupid games, win stupid prizes.",
"Not your keys, not your Bitcoin.",
"Strong hands, long-term thinking.",
"Keep calm and carry on.",
"Ring, Ring, Ring, Ring, Ring, Ring, Ring, Banana Phone!",
"Be the Rolex wearing, diamond ring wearing, kiss stealing, wheeling dealing, "
"limousine riding, jet flying, son of a gun. And I'm having a hard time "
"holding these alligators down. Woo!.",
]


def get_phrase():
    return random.choice(PHRASES)
