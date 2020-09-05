# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import random
import time
import json
import uuid
import logging
import traceback
from base64 import b64encode
from mutagen.mp3 import MP3

from twisted.internet import task, threads

from lightningd import LightningDaemon
from audio_player import AudioPlayer

SECONDS_TO_EXPIRY = 19

CHECK_PERIOD = 1.0

###############################################################################

SONGS = [
    {'path':   "thunder-rolls.mp3",
     'artist': "Garth Brooks",
     'title':  "Thunder Rolls",
     'price':  6.15},
    {'path':   "hustlin.mp3",
     'artist': "Rick Ross",
     'title':  "Hustlin'",
     'price':  6.15},
    {'path':   "mo-money.mp3",
     'artist': "The Notorious B.I.G.",
     'title':  "Mo Money Mo Problems",
     'price':  6.15},
    {'path':   "money.mp3",
     'artist': "Pink Floyd",
     'title':  "Money",
     'price':  6.15},
    {'path':   "riders-on-the-storm.mp3",
     'artist': "The Doors",
     'title':  "Riders On The Storm",
     'price':  6.15},
    {'path':   "thunderstruck.mp3",
     'artist': "AC/DC",
     'title':  "Thunderstruck",
     'price':  6.15},
    {'path':   "ride-the-lightning.mp3",
     'artist': "Metallica",
     'title':  "Ride The Lightning",
     'price':  6.15},
    {'path':   "money-matters.mp3",
     'artist': "S.N.F.U.",
     'title':  "Money Matters",
     'price':  6.15},
    {'path':   "lightning-crashes.mp3",
     'artist': "Live",
     'title':  "Lightning Crashes",
     'price':  6.15},
    {'path':   "money-thats-what-i-want.mp3",
     'artist': "The Supremes",
     'title':  "Money (That's What I Want)",
     'price':  6.15},
    {'path':   "money-money-money.mp3",
     'artist': "ABBA",
     'title':  "Money, Money, Money",
     'price':  6.15},
    {'path':   "c-r-e-a-m.mp3",
     'artist': "Wu Tang Clan",
     'title':  "C.R.E.A.M.",
     'price':  6.15},
    {'path':   "gold-digger.mp3",
     'artist': "Kayne West",
     'title':  "Gold Digger",
     'price':  6.15},
    {'path':   "money-for-nothing.mp3",
     'artist': "Dire Straits",
     'title':  "Money For Nothing",
     'price':  6.15},
    {'path':   "if-i-had-a-million-dollars.mp3",
     'artist': "Barenaked Ladies",
     'title':  "If I Had $1000000",
     'price':  6.15},
    {'path':   "i-get-money.mp3",
     'artist': "50 Cent",
     'title':  "I Get Money",
     'price':  6.15},
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
        return song

    def get_next_song(self):
        self.index -= 1
        if self.index < 0:
            # wrap index
            self.index = len(self.songs) - 2
        i = self.index % len(self.songs)
        s = self.songs[i]
        return s

    def get_prev_song(self):
        self.index += 1
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
        #logging.info("queued: %s %s %s" % (title, artist, path))
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
        self.is_init = False

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
        logging.info("jukebox invoice: %s" % str(result))
        return result['bolt11'], result['expires_at'], label

    ###########################################################################

    def _init_invoices(self):
        try:
            daemon = LightningDaemon(self.daemon_rpc)
            for s in self.music_select.iter_songs():
                bolt11, expires, label = Jukebox._invoice(daemon, s['price'],
                                                          s['title'],
                                                          s['artist'])
                s['bolt11'] = bolt11
                s['expires'] = expires
                s['label'] = label
            self.is_init = True
        except:
            logging.info("ln daemon invoiceing not ready")
            self.reactor.callLater(3.0, self._init_invoices)

    def browse_next_song(self):
        return self.music_select.get_next_song()

    def browse_prev_song(self):
        return self.music_select.get_prev_song()

    ###########################################################################

    def _expired_check(labels_to_check, invoice):
        #logging.info("invoice: %s" % invoice)
        if not invoice['label'] in labels_to_check:
            return False
        if invoice['status'] == 'paid':
            logging.info("paid not expired: %s" % invoice['label'])
            return False
        if invoice['status'] == 'expired':
            logging.info("expired: %s" % invoice['label'])
            return True
        # treat uppaid but near expired as expired
        current_time = int(time.time())
        near = (current_time + SECONDS_TO_EXPIRY) > invoice['expires_at']
        if near:
            logging.info("near: %s" % invoice['label'])
        return near

    def _paid_check(labels_to_check, invoice):
        #logging.info("invoice: %s" % invoice)
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
        try:
            daemon = LightningDaemon(daemon_rpc)
            invs = daemon.get_c_lightning_invoices()
            if not invs:
                return None

            labels_to_check = set(d[0] for d in thread_data if d is not None)
            if len(labels_to_check) != len(SONGS):
                logging.info("labels to check: %s" % labels_to_check)

            paid = set(i['label'] for i in invs['invoices'] if
                       Jukebox._paid_check(labels_to_check, i))
            expired = set(i['label'] for i in invs['invoices'] if
                          Jukebox._expired_check(labels_to_check, i))
            statuses = {i['label']: i['status'] for i in invs['invoices']}
            if len(paid) > 0:
                logging.info("paid invoices: %s" % paid)
            #logging.info("paid: %s" % paid)
            #logging.info("expired: %s" % expired)
            if len(expired) > 0:
                logging.info("expired invoices: %s" % expired)
            renews = list(Jukebox._iter_renews(daemon, thread_data, paid,
                          expired))
            #logging.info("renews %s" % renews)
            if len(renews) > 0:
                logging.info("renew invoices: %s" % renews)
            for l in iter(paid):
                #logging.info("paid deleting: %s" % l)
                s = daemon.delete(l)
                if "code" in s.keys():
                    logging.info(s)
            for l in iter(expired):
                #logging.info("expire deleting: %s" % l)
                status = statuses[l]
                s = daemon.delete(l, state=status)
                if "code" in s.keys():
                    logging.info(s)
            return (paid, renews)
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.exception(e)
            return None


    def _check_paid_callback(self, result):
        #logging.info("got result: %s %s" % (result[0], result[1]))
        if not result:
            logging.error("got exception in check_paid_thread_func")
            self.reactor.callLater(CHECK_PERIOD, self._periodic_check)
            return
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
            self.renewed_cb(old_label, s)

        # TODO - renew websocket/UI clients
        self.reactor.callLater(CHECK_PERIOD, self._periodic_check)

    def _thread_data(self, song):
        if 'label' not in song:
            return None
        # the info needed to check and renew invoices
        return (song['label'], song['title'], song['artist'], song['price'])

    def _check_paid_defer(self):
        thread_data = [self._thread_data(s) for s in
                       self.music_select.iter_songs() if s is not None]
        d = threads.deferToThread(Jukebox._check_paid_thread_func,
                                  self.daemon_rpc, thread_data)
        d.addCallback(self._check_paid_callback)

    ###########################################################################

    def _periodic_check(self):
        #logging.info("invoice checking")
        self._check_paid_defer()

    ###########################################################################

    def set_purchased_cb(self, cb):
        self.purchased_cb = cb

    def set_renewed_cb(self, cb):
        self.renewed_cb = cb

    ###########################################################################

    def run(self):
        self.reactor.callLater(0.5, self._periodic_check)
