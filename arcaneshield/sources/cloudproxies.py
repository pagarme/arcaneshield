import os
import requests
from lxml import html
from tqdm import tqdm

from sources.base import BaseSource

class Source(BaseSource):

    name = 'CloudProxies'

    def get_max_index(self):
        url = 'http://cloudproxies.com/proxylist/?page={page}'

        r = requests.get(url.format(page=1))
        content = r.content
        tree = html.fromstring(content)
        max_index = int(tree.xpath('//*[@class="pagination"]/li/a/@data-ci-pagination-page')[-1])

        return max_index

    def get_length(self):
        return self.get_max_index()

    def get_list(self, q=None):
        url = 'http://cloudproxies.com/proxylist/?page={page}'
        max_index = self.get_max_index()


        for index in range(1, max_index + 1):
            r = requests.get(url.format(page=index))
            content = r.content
            tree = html.fromstring(content)
            ips = tree.xpath('//*[@id="ContentTable"]/tbody/tr/td[3]/text()')

            for ip in ips:
                ip = ip.strip()
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
