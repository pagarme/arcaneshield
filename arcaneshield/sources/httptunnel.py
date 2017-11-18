import os
import requests
from lxml import html
from sources.base import BaseSource

class Source(BaseSource):

    name = 'HTTPTunnel'

    def get_list(self, q=None):
        url = 'http://www.httptunnel.ge/ProxyListForFree.aspx'
        r = requests.get(url,timeout=10)
        tree = html.fromstring(r.content)
        raw = tree.xpath('//*[@target="_new"]/text()')
        ips = [ip.split(':')[0] for ip in raw]

        for ip in ips:
            ip = ip.strip()
            ip = '{}/32'.format(ip)
            if ip not in self.ip_list:
                self.ip_list.append(ip)
                self.pbar.set_postfix(ipcount=str(len(self.ip_list)))
        self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list

    def get_length(self):
        return 1

if __name__ == '__main__':
    s = Source()
    s.get_list()
