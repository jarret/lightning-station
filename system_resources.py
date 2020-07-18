# Copyright (c) 2019 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php
import os
import time
import psutil

from twisted.internet import threads


INTERVAL = 1.5

class SystemResources(object):
    def __init__(self, reactor, screen_ui, blockchain_dir, blockchain_device):
        self.screen_ui = screen_ui
        self.reactor = reactor
        self.blockchain_dir = blockchain_dir
        self.blockchain_device = blockchain_device

        self.d_read, self.d_write = (
            SystemResources.get_disk_counters(blockchain_device))
        self.d_time = time.time()
        self.n_send, self.n_recv = SystemResources.get_net_counters()
        self.n_time = time.time()

    ###########################################################################

    def sum_dir_size(path):
        if not os.path.exists(path):
            return 0
        total_size = os.path.getsize(path)
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += SystemResources.sum_dir_size(itempath)
        return total_size

    ###########################################################################

    def get_ips():
        p = psutil.net_if_addrs()
        for i, addrs in p.items():
            for a in addrs:
                if a[0] == 2:
                    if a[1].startswith("192.168"):
                        yield a[1]
    def get_ip_addr():
        ips = list(SystemResources.get_ips())
        if len(ips) > 0:
            return ips[0]
        return "???"

    ###########################################################################

    def _poll_dir_size_thread_func(blockchain_dir):
        return {'dir_size': SystemResources.sum_dir_size(blockchain_dir)}

    def _poll_dir_size_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(30, self._poll_dir_size_defer)

    def _poll_dir_size_defer(self):
        d = threads.deferToThread(SystemResources._poll_dir_size_thread_func,
                                  self.blockchain_dir)
        d.addCallback(self._poll_dir_size_callback)

    ###########################################################################

    def _poll_ip_thread_func():
        return {'ip_address': SystemResources.get_ip_addr()}

    def _poll_ip_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(30, self._poll_ip_defer)

    def _poll_ip_defer(self):
        d = threads.deferToThread(SystemResources._poll_ip_thread_func)
        d.addCallback(self._poll_ip_callback)

    ###########################################################################

    def _poll_cpu_thread_func():
        cpu = psutil.cpu_percent(percpu=True)
        cpu.sort()
        cpu.reverse()
        return {'cpu_pct': cpu}

    def _poll_cpu_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(0.8, self._poll_cpu_defer)

    def _poll_cpu_defer(self):
        d = threads.deferToThread(SystemResources._poll_cpu_thread_func)
        d.addCallback(self._poll_cpu_callback)

    ###########################################################################

    def _poll_memory_thread_func():
        vm = psutil.virtual_memory()
        total = vm.total
        used = vm.total - vm.available
        used_pct = ((1.0 - (float(vm.available) / float(vm.total))) * 100.0)
        return {'mem_total':    total,
                'mem_used':     used,
                'mem_used_pct': used_pct}

    def _poll_memory_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(0.8, self._poll_memory_defer)

    def _poll_memory_defer(self):
        d = threads.deferToThread(SystemResources._poll_memory_thread_func)
        d.addCallback(self._poll_memory_callback)

    ###########################################################################

    def get_net_counters():
        n = psutil.net_io_counters()
        return n.bytes_sent, n.bytes_recv

    def _poll_net_thread_func():
        s, r = SystemResources.get_net_counters()
        t = time.time()
        return {'send': s,
                'recv': r,
                'time': t}

    def _poll_net_callback(self, result):
        elapsed = result['time'] - self.n_time
        send_rate = int((result['send'] - self.n_send) / elapsed)
        recv_rate = int((result['recv'] - self.n_recv) / elapsed)
        self.n_send = result['send']
        self.n_recv = result['recv']
        self.n_time = result['time']
        self.screen_ui.update_info({'net_send': send_rate,
                                    'net_recv': recv_rate})
        self.reactor.callLater(0.8, self._poll_net_defer)

    def _poll_net_defer(self):
        d = threads.deferToThread(SystemResources._poll_net_thread_func)
        d.addCallback(self._poll_net_callback)

    ###########################################################################

    def get_disk_counters(blockchain_device):
        c = psutil.disk_io_counters(perdisk=True)[blockchain_device]
        return c.read_bytes, c.write_bytes

    def _poll_disk_thread_func(blockchain_device):
        r, w = SystemResources.get_disk_counters(blockchain_device)
        t = time.time()
        return {'read':  r,
                'write': w,
                'time':  t}

    def _poll_disk_callback(self, result):
        elapsed = result['time'] - self.d_time
        read_rate = int((result['read'] - self.d_read) / elapsed)
        write_rate = int((result['write'] - self.d_write) / elapsed)
        self.d_read = result['read']
        self.d_write = result['write']
        self.d_time = result['time']
        self.screen_ui.update_info({'disk_read':  read_rate,
                                    'disk_write': write_rate})
        self.reactor.callLater(0.8, self._poll_disk_defer)

    def _poll_disk_defer(self):
        d = threads.deferToThread(SystemResources._poll_disk_thread_func,
                                  self.blockchain_device)
        d.addCallback(self._poll_disk_callback)

    ###########################################################################

    def run(self):
        #self.reactor.callLater(0.5, self._poll_system_resources_defer)
        self.reactor.callLater(2.0, self._poll_memory_defer)
        self.reactor.callLater(2.0, self._poll_cpu_defer)
        self.reactor.callLater(2.0, self._poll_disk_defer)
        self.reactor.callLater(2.0, self._poll_net_defer)
        self.reactor.callLater(2.0, self._poll_dir_size_defer)
        self.reactor.callLater(2.0, self._poll_ip_defer)
