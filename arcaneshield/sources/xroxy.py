import os
import requests
from lxml import html
from sources.base import BaseSource

class Source(BaseSource):
    name = 'Xroxy'

    def get_length(self):
        return int(self.get_max())

    def get_list(self, q):
        max_index = int(self.get_max())
        for index in range(0,max_index+1):
            tree = self.connect(index)
            raw = tree.xpath('//*[@title="View this Proxy details"]/text()')
            ips = [ip.strip() for ip in raw if ip.strip()]
            for ip in ips:
                if ip not in self.ip_list:
                    self.ip_list.append(ip)
                self.pbar.set_postfix(ipcount=str(len(self.ip_list)))
            self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list


    def connect(self,index):
        url = 'http://www.xroxy.com/proxylist.php?pnum=%d' % index
        r = requests.get(url,timeout=10)
        tree = html.fromstring(r.text)
        return tree

    def get_max(self,):
        tree = self.connect(0)
        max_index = int(tree.xpath('//*[@id="content"]/table[2]/tr/td[1]/table/tr[2]/td/small/b/text()')[0])/10
        return max_index

if __name__ == '__main__':
    s = Source()
    s.get_list()
