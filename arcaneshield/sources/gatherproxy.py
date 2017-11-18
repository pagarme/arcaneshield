#www.gatherproxy.com
import os
import requests
from lxml import html
from threading import Thread, Lock, BoundedSemaphore
from sources.base import BaseSource
from tqdm import tqdm
from time import sleep

class Source(BaseSource): 

    name = 'GatherProxy'

    def __init__(self): 
        self.ip_list = []
        self.lock = Lock()
        self.pbar_lock = Lock()
        self.sema = BoundedSemaphore(value=10)


    def get_list(self, q=None): 
        countries = self.get_countries()

        tl = []
        for country in countries: 
            t = Thread(target=self.proxy_by_country, args=(country, ))
            t.start()
            tl.append(t)

        for t in tl:
            t.join()

        if q:
            q.put(self.ip_list)

        return self.ip_list

    def proxy_by_country(self, country): 
        with self.sema:
            country = country.strip()
            max_index = self.total_pages(country)
            for index in range(1, max_index + 1):
                self.get_proxies(country, index)
            self.pbar_lock.acquire()
            self.pbar.update(1)
            self.pbar_lock.release()

    def get_countries(self, ): 
        url = 'http://www.gatherproxy.com/proxylistbycountry'
        r = requests.get(url, timeout=10)
        tree = html.fromstring(r.content)
        countries = [country.split('(')[0] for country in tree.xpath('//*[@class="pc-list"]/li/a/text()')]
        return countries

    def connect(self, country, index): 
        url = 'http://www.gatherproxy.com/proxylist/country/?c=%s' % country
        data = {'Country': country, 'Filter': '', 'PageIdx': index, 'Uptime': 0}
        r = requests.post(url, data=data, timeout=10)
        return r.content

    def total_pages(self, country): 
        try: 
            content = self.connect(country, 1)
            tree = html.fromstring(content)
            max_index = tree.xpath('//*[@id="psbform"]/div/a/text()')
            if max_index: 
                return int(max_index[-1])
            else: 
                return 0
        except Exception as e: 
            pass

    def get_length(self):
        return len(self.get_countries())

    def get_proxies(self, country, index): 
        content = self.connect(country, index)
        tree = html.fromstring(content)
        try: 
            ips = [ip.split("document.write('")[1].split("')")[0] for ip in tree.xpath('//*[@id="tblproxy"]/tr/td[2]/script/text()')]
            self.lock.acquire()
            for ip in ips: 
                ip = ip.strip()
                ip = '{}/32'.format(ip)
                if ip not in self.ip_list: 
                    self.ip_list.append(ip)
                self.pbar.set_postfix(ipcount=str(len(self.ip_list)))
            self.lock.release()
        except Exception as e: 
            pass

if __name__ == '__main__': 
    s = Source()
    s.get_list()
    print(s.ip_list)
