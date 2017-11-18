#http://torstatus.blutmagie.de

import os
import requests
from lxml import html
from sources.base import BaseSource

class Source(BaseSource):

    name = 'Tor'

    def get_length(self):
        return 1

    def get_list(self, q):
        r = requests.get('https://check.torproject.org/exit-addresses', timeout=10)

        lines = r.text.split('\n')

        torNodes = []

        for line in lines:
            if line.startswith('ExitAddress'):
                torNodes.append(line.split()[1])

        for ip in torNodes:
            if ip not in self.ip_list:
                self.ip_list.append(ip)
            self.pbar.set_postfix(ipcount=str(len(self.ip_list)))

        self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list

if __name__ == '__main__':
    s = Source()
    s.get_list()
