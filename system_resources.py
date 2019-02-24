import os
import psutil

from twisted.internet import threads


INTERVAL = 2.0

class SystemResources(object):
    def __init__(self, reactor, screen_ui, blockchain_dir, blockchain_device):
        self.screen_ui = screen_ui
        self.reactor = reactor
        self.blockchain_dir = blockchain_dir
        self.blockchain_device = blockchain_device

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

    def _poll_system_resources_thread_func(blockchain_dir, blockchain_device):
        sr = {}
        vm = psutil.virtual_memory()
        sr['mem_total'] = vm.total
        sr['mem_used'] = vm.total - vm.available
        #sr['mem_available'] = vm.available
        sr['mem_used_pct'] = ((1.0 - (float(vm.available) / float(vm.total))) *
                              100.0)
        start_disk = psutil.disk_io_counters(perdisk=True)[blockchain_device]
        start_net = psutil.net_io_counters()
        sr['cpu_pct'] = psutil.cpu_percent(interval=INTERVAL, percpu=True)
        sr['cpu_pct'].sort()
        sr['cpu_pct'].reverse()
        end_disk = psutil.disk_io_counters(perdisk=True)[blockchain_device]
        end_net = psutil.net_io_counters()
        read = int((end_disk.read_bytes - start_disk.read_bytes) / INTERVAL)
        write = int((end_disk.write_bytes - start_disk.write_bytes) / INTERVAL)
        sr['disk_read'] = read
        sr['disk_write'] = write
        send = int((end_net.bytes_sent - start_net.bytes_sent) / INTERVAL)
        recv = int((end_net.bytes_recv - start_net.bytes_recv) / INTERVAL)
        sr['net_send'] = send
        sr['net_recv'] = recv
        sr['dir_size'] = SystemResources.sum_dir_size(blockchain_dir)
        sr['ip_address'] = SystemResources.get_ip_addr()
        return sr

    def _poll_system_resources_callback(self, result):
        self.screen_ui.update_info(result)
        self.reactor.callLater(0.0, self._poll_system_resources_defer)

    def _poll_system_resources_defer(self):
        d = threads.deferToThread(
            SystemResources._poll_system_resources_thread_func,
            self.blockchain_dir, self.blockchain_device)
        d.addCallback(self._poll_system_resources_callback)

    ###########################################################################

    def run(self):
        self.reactor.callLater(0.5, self._poll_system_resources_defer)
