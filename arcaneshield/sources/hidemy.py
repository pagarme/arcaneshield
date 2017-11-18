import os
import requests
from lxml import html
from sources.base import BaseSource
import cfscrape

class Source(BaseSource):
    name = 'Hidemy'

    def get_list(self, q):
        try:
            max_index, total_pages = self.get_index()
            for x in range(0, max_index, max_index/total_pages):
                try:
                    content = self.connect(x)
                    tree = html.fromstring(content)
                    ips = tree.xpath('//*[@class="tdl"]/text()')
                    #ports = tree.xpath('//*[@id="content-section"]/section[1]/div/table/tbody/tr/td[2]/text()')
                    for ip in ips:
                        ip = ip.strip()
                        if ip not in self.ip_list:
                            self.ip_list.append(ip)
                            self.pbar.set_postfix(ipcount=str(len(self.ip_list)))
                except:
                    continue
                self.pbar.update(max_index/total_pages)
        except Exception as e:
            pass

        if q:
            q.put(self.ip_list)

        return self.ip_list

    def get_length(self):
        m,  t = self.get_index()
        return m

    def connect(self, index):
        url = 'https://hidemy.name/en/proxy-list/?start=%d' % index
        scraper = cfscrape.create_scraper()
        r = scraper.get(url, timeout=10)
        return r.content

    def get_index(self, ):
        content = self.connect(0)
        tree = html.fromstring(content)
        max_index = tree.xpath('//*[@id="content-section"]/section[1]/div/div[4]/ul/li/a/@href')[-1].split('=')[1].split('#')[0]
        total_pages = tree.xpath('//*[@id="content-section"]/section[1]/div/div[4]/ul/li/a/text()')[-1]
        return int(max_index), int(total_pages)

if __name__ == '__main__':
    s = Source()
    s.get_list()
