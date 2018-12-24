import os
import random

SONGS = [
    {'path':   "never-gonna-give-you-up.mp3",
     'artist': "Rick Astley",
     'title':  "Never Gonna Give You Up",
     'price':  123},
    {'path':   "banana-phone.mp3",
     'artist': "Raffi",
     'title':  "Banana Phone",
     'price':  321},
    {'path':   "thunder-rolls.mp3",
     'artist': "Garth Brooks",
     'title':  "Thunder Rolls",
     'price':  222},
    {'path':   "thunderstruck.mp3",
     'artist': "AC/DC",
     'title':  "Thunderstruck",
     'price':  333},
    {'path':   "friday.mp3",
     'artist': "Rebecca Black",
     'title':  "Friday",
     'price':  555},
]

MOCK_BOLT11 = "lnbc50n1pdm373mpp50hlcjdrcm9u3qqqs4a926g63d3t5qwyndytqjjgknskuvmd9kc2sdz2d4shyapwwpujq6twwehkjcm9ypnx7u3qxys8q6tcv4k8xtpqw4ek2ujlwd68y6twvuazqg3zyqxqzjcuvzstexcj4zcz7ldtkwz8t5pdsghauyhkdqdxccx8ts3ta023xqzwgwxuvlu9eehh97d0qcu9k5a4u2glenrekp7w9sswydl4hneyjqqzkxf54"

class MusicSelect(object):
    def __init__(self, music_dir):
        self.music_dir = music_dir
        self.songs = [self.fill_song(s) for s in SONGS]
        self.index = random.randint(0, len(self.songs))

    def fill_song(self, song):
        full = os.path.join(self.music_dir, song['path'])
        assert os.path.exists(full), "could not locate? %s" % full
        song['path'] = full
        song['bolt11'] = MOCK_BOLT11
        return song

    def get_next_song(self):
        i = self.index % len(self.songs)
        s = self.songs[i]
        self.index += 1
        return s
