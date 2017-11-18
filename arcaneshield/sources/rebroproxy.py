import os
import requests
from sources.base import BaseSource

class Source(BaseSource):
    name = 'RebroProxy'

    def get_length(self):
        return 1

    def get_list(self, q):
        url = 'http://rebro.weebly.com/uploads/2/7/3/7/27378307/rebroproxy-all-113326062014.txt'
        r = requests.get(url,timeout=10)
        ips = list()
        for raw in r.text.split():
            ip = raw.split(':')[0]
            if ip not in self.ip_list:
                self.ip_list.append(ip)
                self.pbar.set_postfix(ipcount=str(len(self.ip_list)))

        self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list

if __name__ == '__main__':
    rebroproxy()
