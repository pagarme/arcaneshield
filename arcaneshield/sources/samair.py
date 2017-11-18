import os
import requests
from lxml import html
from sources.base import BaseSource

class Source(BaseSource):
    name = 'Samair'

    def get_length(self):
        return self.max_index()

    def get_list(self, q):
        max_index = self.max_index()
        for index in range(0,max_index+1):
            self.get(index)
            self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list

    def max_index(self,):
        url = "http://samair.ru/proxy/"
        r = requests.get(url,timeout=10)
        tree = html.fromstring(r.content)
        indexes = tree.xpath('//*[@id="navbar"]/ul/li/a/text()')
        indexes.pop()
        return int(indexes[-1])

    def get(self,index):
        url = 'http://samair.ru/proxy/list-IP-port/proxy-%d.htm' % index
        r = requests.get(url,timeout=10)
        tree = html.fromstring(r.content)
        raw = tree.xpath('//div[@class="singleprice order-msg"]/pre/text()')
        if raw:
            raw.pop(0)
            raw = raw[0].split('\n')
            ips = [ip.split(':')[0] for ip in raw if ip]
            for ip in ips:
                if ip not in self.ip_list:
                    self.ip_list.append(ip)
                    self.pbar.set_postfix(ipcount=str(len(self.ip_list)))

if __name__ == '__main__':
    s = Source()
    s.get_list()
