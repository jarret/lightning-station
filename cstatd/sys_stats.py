# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import psutil

class SysStats():
    @staticmethod
    def get_ips():
        p = psutil.net_if_addrs()
        for i, addrs in p.items():
            for a in addrs:
                if a[0] == 2:
                    if a[1].startswith("192.168"):
                        yield a[1]

    @staticmethod
    def get_net_stats():
        ips = list(SysStats.get_ips())
        if len(ips) > 0:
            return [('ip_addr', ips[0])]
        return [('ip_addr', "???")]

    @staticmethod
    def get_cpu_stats():
        cpu = psutil.cpu_percent(percpu=True)
        cpu.sort()
        cpu.reverse()
        return [('cpu_pct', cpu)]

    @staticmethod
    def get_mem_stats():
        vm = psutil.virtual_memory()
        total = vm.total
        used = vm.total - vm.available
        used_pct = ((1.0 - (float(vm.available) / float(vm.total))) * 100.0)
        return [('mem_total',    total),
                ('mem_used',     used),
                ('mem_used_pct', used_pct)]

    @staticmethod
    def fetch_stats():
        cpu = SysStats.get_cpu_pct()
        ip = SysStats.get_net_stats()
        mem = SysStats.get_mem_stats()
        return cpu + ip + mem
