import os
import shutil
import subprocess
from logger import log
from twisted.internet import threads


SOUND_EFFECTS = {
    'block':  'audio_files/light.mp3',
    'button': 'audio_files/pull-out.mp3',
}

for p in SOUND_EFFECTS.values():
    path = os.path.abspath(p)
    assert os.path.exists(p), "no file? %s" % path


CMDS = [
    ['omxplayer', '-i', 'local'],
    ['mpg123-pulse'],
]

###############################################################################

class AudioPlayer(object):
    def __init__(self):
        self.cmd = None
        for cmd in CMDS:
            if self._cmd_exists(cmd[0]):
                self.cmd = cmd
                break
        log(self.cmd)

    def _cmd_exists(self, cmd):
        return shutil.which(cmd) is not None

    ###########################################################################

    def _play_thread_func(cmd, path):
        p = subprocess.Popen(cmd + [path], stderr=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
        p.wait()
        return None

    def _play_callback(self, result):
        pass

    def _play_defer(self, path):
        d = threads.deferToThread(AudioPlayer._play_thread_func,
                                  self.cmd, path)
        d.addCallback(self._play_callback)

    ###########################################################################

    def play(self, path):
        self._play_defer(path)

    def play_and_wait(self, path):
        p = subprocess.Popen(self.cmd + [path], stderr=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
        p.wait()

    ###########################################################################

    def play_sound_effect(self, effect):
        path = SOUND_EFFECTS[effect]
        self.play(path)

    def play_song(self, path):
        self.play_and_wait(path)
