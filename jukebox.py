import os
import random
import time
import json
import uuid
from base64 import b64encode
from mutagen.mp3 import MP3

from twisted.internet import task, threads

from lightningd import LightningDaemon
from audio_player import AudioPlayer
from logger import log

EXPIRY = 60 * 60 * 24 # 24 hours

SECONDS_TO_EXPIRY = 30

CHECK_PERIOD = 1.0

###############################################################################

SONGS = [
#    {'path':   "never-gonna-give-you-up.mp3",
#     'artist': "Rick Astley",
#     'title':  "Never Gonna Give You Up",
#     'price':  11.123},
#    {'path':   "banana-phone.mp3",
#     'artist': "Raffi",
#     'title':  "Banana Phone",
#     'price':  10.321},
    {'path':   "thunder-rolls.mp3",
     'artist': "Garth Brooks",
     'title':  "Thunder Rolls",
     'price':  14.456},
    {'path':   "hustlin.mp3",
     'artist': "Rick Ross",
     'title':  "Hustlin'",
     'price':  22.222},
    {'path':   "mo-money.mp3",
     'artist': "The Notorious B.I.G.",
     'title':  "Mo Money Mo Problems",
     'price':  14.141},
    {'path':   "bitcoin-cash.mp3",
     'artist': "Lil Windex",
     'title':  "Bitcoin Ca$h",
     'price':  0.001},
    {'path':   "money.mp3",
     'artist': "Pink Floyd",
     'title':  "Money",
     'price':  12.345},
    {'path':   "riders-on-the-storm.mp3",
     'artist': "The Doors",
     'title':  "Riders On The Storm",
     'price':  13.777},
    {'path':   "thunderstruck.mp3",
     'artist': "AC/DC",
     'title':  "Thunderstruck",
     'price':  11.333},
    #{'path':   "friday.mp3",
    # 'artist': "Rebecca Black",
    # 'title':  "Friday",
    # 'price':  12.555},
    {'path':   "ride-the-lightning.mp3",
     'artist': "Metallica",
     'title':  "Ride The Lightning",
     'price':  13.123},
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
        audio = MP3(song['path'])
        song['length'] = audio.info.length
        print(song)
        return song

    def get_next_song(self):
        self.index += 1
        i = self.index % len(self.songs)
        s = self.songs[i]
        return s

    def get_prev_song(self):
        self.index -= 1
        if self.index < 0:
            # wrap index
            self.index = len(self.songs) - 2
        i = self.index % len(self.songs)
        s = self.songs[i]
        return s

    def iter_songs(self):
        for s in self.songs:
            yield s


###############################################################################

class JukeboxQueue(object):
    def __init__(self, screen_ui):
        self.screen_ui = screen_ui
        self.song_queue = []
        self.queue_running = False
        self.song_playing = None

    ###########################################################################

    def _play_song_thread_func(path):
        a = AudioPlayer()
        a.play_song(path)
        return None

    def _play_song_callback(self, result):
        self._finish_playing_song()

    def _play_song_defer(self, path):
        self.song_start_time = time.time()
        d = threads.deferToThread(JukeboxQueue._play_song_thread_func, path)
        d.addCallback(self._play_song_callback)

    ###########################################################################

    def _finish_playing_song(self):
        self.queue_running = False
        self.song_playing = None
        self._try_next()
        self._update_screen()

    def _try_next(self):
        if (self.queue_running == False) and (len(self.song_queue) > 0):
            self.queue_running = True
            song = self.song_queue.pop(0)
            self.song_playing = song
            self._play_song_defer(song['path'])

    ###########################################################################

    def _update_screen(self):
        spt = self.song_playing['title'] if self.song_playing else None
        spa = self.song_playing['artist'] if self.song_playing else None
        sst = self.song_start_time if self.song_playing else None
        sl = self.song_playing['length'] if self.song_playing else None
        info = {'song_playing_title':  spt,
                'song_playing_artist': spa,
                'song_start_time':     sst,
                'song_length':         sl,
                'queued_songs':        []}
        for s in self.song_queue:
            info['queued_songs'].append({'title':  s['title'],
                                         'artist': s['artist']})
        self.screen_ui.update_info(info)

    def add_song(self, title, artist, path, length):
        log("queued: %s %s %s" % (title, artist, path))
        self.song_queue.append({'title':  title,
                                'artist': artist,
                                'length': length,
                                'path':   path})
        self._try_next()
        self._update_screen()

###############################################################################

class Jukebox(object):
    def __init__(self, reactor, screen_ui, music_dir, daemon_rpc):
        self.queue = []
        self.purchased_cb = None
        self.renewed_cb = None
        self.reactor = reactor
        self.music_select = MusicSelect(music_dir)
        self.daemon_rpc = daemon_rpc
        self.jukebox_queue = JukeboxQueue(screen_ui)
        self._init_invoices()

    ###########################################################################

    def _gen_new_label():
        label_bytes = uuid.uuid4().bytes
        label_str = b64encode(label_bytes).decode('utf8')
        return label_str

    def _invoice(daemon, price, title, artist):
        label = Jukebox._gen_new_label()
        msatoshis = int(price * 1000)
        description = "Jukebox play: %s - %s" % (title, artist)
        result = daemon.invoice_c_lightning(msatoshis, label, description)
        return result['bolt11'], result['expires_at'], label

    ###########################################################################

    def _init_invoices(self):
        daemon = LightningDaemon(self.daemon_rpc)
        for s in self.music_select.iter_songs():
            bolt11, expires, label = Jukebox._invoice(daemon, s['price'],
                                                      s['title'],
                                                      s['artist'])
            s['bolt11'] = bolt11
            s['expires'] = expires
            s['label'] = label

    def browse_next_song(self):
        return self.music_select.get_next_song()

    def browse_prev_song(self):
        return self.music_select.get_prev_song()

    ###########################################################################

    def _expired_check(labels_to_check, invoice):
        #log("invoice: %s" % invoice)
        if not invoice['label'] in labels_to_check:
            return False
        if invoice['status'] == 'paid':
            return False
        if invoice['status'] == 'expired':
            return True
        # treat uppaid but near expired as expired
        current_time = int(time.time())
        return (current_time + SECONDS_TO_EXPIRY) > invoice['expires_at']

    def _paid_check(labels_to_check, invoice):
        #log("invoice: %s" % invoice)
        if not invoice['label'] in labels_to_check:
            return False
        return invoice['status'] == 'paid'

    def _iter_renews(daemon, thread_data, paid, expired):
        for label, title, artist, price in thread_data:
            if (label in paid) or (label in expired):
                old_label = label
                bolt11, expires, new_label = Jukebox._invoice(daemon, price,
                                                              title, artist)
                yield (old_label, new_label, bolt11, expires)

    def _check_paid_thread_func(daemon_rpc, thread_data):
        daemon = LightningDaemon(daemon_rpc)
        invs = daemon.get_c_lightning_invoices()
        labels_to_check = set(d[0] for d in thread_data)
        paid = set(i['label'] for i in invs['invoices'] if
                   Jukebox._paid_check(labels_to_check, i))
        expired = set(i['label'] for i in invs['invoices'] if
                      Jukebox._expired_check(labels_to_check, i))
        log("paid: %s" % paid)
        log("expired: %s" % expired)
        renews = list(Jukebox._iter_renews(daemon, thread_data, paid, expired))
        log("renews %s" % renews)
        for l in iter(paid):
            log("paid deleting: %s" % l)
            daemon.delete(l)
        for l in iter(expired):
            log("expire deleting: %s" % l)
            daemon.delete(l, state="unpaid")
        return (paid, renews)

    def _check_paid_callback(self, result):
        log("got result: %s %s" % (result[0], result[1]))
        paid, renews = result
        songs = {s['label']: s for s in self.music_select.iter_songs()}
        for l in iter(paid):
            if l not in songs:
                continue
            self.jukebox_queue.add_song(songs[l]['title'],
                                        songs[l]['artist'],
                                        songs[l]['path'],
                                        songs[l]['length'])
            self.purchased_cb(songs[l]['price'])

        for old_label, new_label, bolt11, expires in renews:
            s = songs[old_label]
            s['label'] = new_label
            s['bolt11'] = bolt11
            s['expires'] = expires
            self.renewed_cb(old_label, songs[l])

        # TODO - renew websocket/UI clients
        self.reactor.callLater(CHECK_PERIOD, self._periodic_check)

    def _thread_data(self, song):
        # the info needed to check and renew invoices
        return (song['label'], song['title'], song['artist'], song['price'])

    def _check_paid_defer(self):
        thread_data = [self._thread_data(s) for s in
                       self.music_select.iter_songs()]
        d = threads.deferToThread(Jukebox._check_paid_thread_func,
                                  self.daemon_rpc, thread_data)
        d.addCallback(self._check_paid_callback)

    ###########################################################################

    def _periodic_check(self):
        log("invoice checking")
        self._check_paid_defer()

    ###########################################################################

    def set_purchased_cb(self, cb):
        self.purchased_cb = cb

    def set_renewed_cb(self, cb):
        self.renewed_cb = cb

    ###########################################################################

    def run(self):
        self.reactor.callLater(0.5, self._periodic_check)
