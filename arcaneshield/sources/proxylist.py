import os
import base64
import requests
from lxml import html
from sources.base import BaseSource

class Source(BaseSource):
    name = 'ProxyList'

    def get_length(self):
        return self.get_max()

    def get_list(self, q):
        maxIndex = self.get_max()
        for index in range(0,maxIndex+1):
            self.get_proxy(index)
            self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list

    def connect(self,index):
        url = 'https://proxy-list.org/english/index.php?p=%d' % index
        r = requests.get(url,timeout=10)
        tree = html.fromstring(r.text)
        return tree

    def get_max(self,):
        tree = self.connect(1)
        indexes = tree.xpath('//*[@id="content"]/div[4]/div[5]/div[2]/a/text()')
        indexes.pop()
        return int(indexes[-1])

    def get_proxy(self,index):
        tree = self.connect(index)
        raw = [base64.b64decode(ip.split("('")[1].split("')")[0]) for ip in tree.xpath('//*[@class="proxy"]/script/text()')]
        ips = list()
        for info in raw:
            ip = info.decode().split(':')[0]
            ip = '{}/32'.format(ip)
            if ip not in self.ip_list:
                self.ip_list.append(ip)
            self.pbar.set_postfix(ipcount=str(len(self.ip_list)))


if __name__ == '__main__':
    s = Source()
    s.get_list()
