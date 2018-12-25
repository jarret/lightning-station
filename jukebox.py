import json
import uuid
from base64 import b64encode

from twisted.internet import task, threads
from lightning import LightningRpc

from music_select import MusicSelect
from audio_player import AudioPlayer
from logging import log

EXPIRY = 60 * 60

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


class Jukebox(object):
    def __init__(self, reactor, music_dir, daemon_rpc):
        self.queue = []
        self.reactor = reactor
        self.music_select = MusicSelect(music_dir)
        self.audio_player = AudioPlayer()
        self.daemon = Daemon(daemon_rpc)
        self._init_invoices()

###############################################################################

    def _gen_new_label(self):
        label_bytes = uuid.uuid4().bytes
        label_str = b64encode(label_bytes).decode('utf8')
        return label_str

    def _init_invoice(self, song):
        msatoshis = int(song['price'] * 1000)
        label = self._gen_new_label()
        description = "play: %s - %s" % (song['title'], song['artist'])
        result = self.daemon.invoice_c_lightning(msatoshis, label, description)
        song['bolt11'] = result['bolt11']
        song['expires'] = result['expires']
        song['label'] = label

    def _init_invoices(self):
        for s in self.music_select.iter_songs():
            self._init_invoice(s)

    def browse_next_song(self):
        return self.music_select.get_next_song()

    ###########################################################################

    def _expire_check(invoice):

    def _check_paid_thread_func(labels):
        invoices = self.daemon.get_c_lightning_invoices()
        paid_labels = set(i['label'] for i in invoices if i['state'] == 'paid')
        expired_labels = set(i['label'] for i in invoices if
                             Jukebox._expired_check(i))
        # TODO spin new invoices, deleted paid
        paid = list(set(labels).intersection(paid_labels))

        replacements = {}

        return {'paid':    paid,
                'replace': replacements}

    def _check_paid_callback(self, result):
        paid_labels = result
        songs = {s['label']: s for s in self.music_select.iter_songs()}
        for paid_label in paid_labels:
            paid_song = songs[paid_label]
            log(json.dumps(paid_song, sort_keys=True))
            #TODO queue songs for playing
            # display queued song list

        self.reactor.callLater(CHECK_PERIOD, self._periodic_check)

    def _check_paid_defer(self):
        labels = [s['label'] for s in self.music_select.iter_songs()]
        d = thread.deferToThread(Jukebox._check_paid_thread_func, labels)
        d.addCallback(self._check_paid_callback)

    ###########################################################################

    def _periodic_check(self):
        self._check_paid_defer()

    ###########################################################################

    def run(self):
        self.reactor.callLater(0.5, self._periodic_check)
