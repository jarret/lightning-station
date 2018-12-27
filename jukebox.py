import json
import uuid
from base64 import b64encode

from twisted.internet import task, threads
from lightning import LightningRpc

from music_select import MusicSelect
from audio_player import AudioPlayer
from logging import log

EXPIRY = 60 * 60 * 24 # 24 hours

SECONDS_TO_EXPIRY = 30

CHECK_PERIOD = 1.0


class Daemon(object):
    def __init__(self, daemon_rpc):
        self.rpc = LightningRpc(daemon_rpc)


    def invoice_c_lightning(self, msatoshi, label, description):
        result = self.rpc.invoice(msatoshi, label, description,
                                  expiry=EXPIRY)
        print(json.dumps(result, indent=1, sort_keys=True))
        return result

    def get_c_lightning_invoices(self):
        result = self.rpc.listinvoices()
        print(json.dumps(result, indent=1, sort_keys=True))
        return result

    def delete(self, label):
        result = self.rpc.delinvoice(label, "paid")
        print(json.dumps(result, indent=1, sort_keys=True))
        return result

###############################################################################

class Jukebox(object):
    def __init__(self, reactor, music_dir, daemon_rpc):
        self.queue = []
        self.reactor = reactor
        self.music_select = MusicSelect(music_dir)
        self.audio_player = AudioPlayer()
        self.daemon_rpc = daemon_rpc
        self._init_invoices()

    ###########################################################################

    def _gen_new_label():
        label_bytes = uuid.uuid4().bytes
        label_str = b64encode(label_bytes).decode('utf8')
        return label_str

    def _invoice(daemon, price, title, artist):
        label = Jukebox._gen_new_label()
        msatoshis = int(price * 1000)
        description = "play: %s - %s" % title, artist)
        result = daemon.invoice_c_lightning(msatoshis, label, description)
        return result['bolt11'], result['expires'], label

    ###########################################################################

    def _init_invoices(self):
        daemon = Daemon(self.daemon_rpc)
        for s in self.music_select.iter_songs():
            bolt11, expires, label = Jukebox._invoice(daemon, s['price'],
                                                      s['title'],
                                                      s['artist'])
            s['bolt11'] = bolt11
            s['expires'] = expires
            s['label'] = label

    def browse_next_song(self):
        return self.music_select.get_next_song()

    ###########################################################################

    def _expire_check(labels_to_check, invoice):
        if not invoice['label'] in labels_to_check:
            return False
        if invoice['state'] == 'paid':
            return False
        if invoice['state'] == 'expired':
            return True
        # treat uppaid but near expired as expired
        current_time = int(time.time())
        return (current_time + SECONDS_TO_EXPIRY) > invoice['expiry']

    def _paid_check(labels_to_check, invoice):
        if not invoice['label'] in labels_to_check:
            return False
        return invoice['state'] == 'paid'

    def _iter_renews(daemon, thread_data, paid, expired):
        for label, title, artist, price in thread_data:
            if (label in paid) or (label in expired):
                old_label = label
                bolt11, expires, new_label = Jukebox._invoice(daemon, price,
                                                              title, artist)
                yield (old_label, new_label, bolt11, expires)

    def _check_paid_thread_func(daemon_rpc, thread_data):
        daemon = Daemon(daemon_rpc)
        invs = daemon.get_c_lightning_invoices()
        labels_to_check = set(d[0] for d in thread_data)
        paid = set(i['label'] for i in invs if
                   Jukebox_paid_check(labels_to_check, i))
        expired = set(i['label'] for i in invs if
                      Jukebox._expired_check(labels_to_check, i))

        renews = set(Jukebox._iter_renews(daemon, thread_data, paid, expired))
        for l in iter(paid):
            daemon.delete(l)
        for l in iter(expired):
            daemon.delete(l)
        return (paid, renews)

    def _check_paid_callback(self, result):
        paid, renews = result
        songs = {s['label']: s for s in self.music_select.iter_songs()}
        for l in iter(paid):
            if l not songs:
                continue
            log("QUEUE: %s" % s['path'])
            # TODO:- implement queue
            # TODO - kick off queue playing

        for old_label, new_label, bolt11, expires in renews:
            s = songs['old_label']
            s['label'] = new_label
            s['bolt11'] = bolt11
            s['expires'] = expires

        # TODO - renew websocket/UI clients
        self.reactor.callLater(CHECK_PERIOD, self._periodic_check)

    def _thread_data(self, song):
        # the info needed to check and renew invoices
        return (song['label'], song['title'], song['artist'], song['price'])

    def _check_paid_defer(self):
        thread_data = [self._thread_data(s) for s in
                       self.music_select.iter_songs()]
        d = thread.deferToThread(Jukebox._check_paid_thread_func,
                                 self.daemon_rpc, thread_data)
        d.addCallback(self._check_paid_callback)

    ###########################################################################

    def _periodic_check(self):
        self._check_paid_defer()

    ###########################################################################

    def run(self):
        self.reactor.callLater(0.5, self._periodic_check)
