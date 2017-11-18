#https://nordvpn.com/

import os
import requests
from sources.base import BaseSource

class Source(BaseSource):
    name = 'NordVPN'

    def get_length(self):
        return 1

    def get_list(self, q=None):
        url = 'https://nordvpn.com/wp-admin/admin-ajax.php?searchParameters[0][name]=proxy-country&searchParameters[0][value]=&searchParameters[1][name]=proxy-ports&searchParameters[1][value]=&offset=0&limit=100000&action=getProxies'
        r = requests.get(url,timeout=10)

        for proxy in r.json():
            if proxy['ip'] not in self.ip_list:
                self.ip_list.append(proxy['ip'])
                self.pbar.set_postfix(ipcount=str(len(self.ip_list)))

        self.pbar.update(1)

        if q:
            q.put(self.ip_list)

        return self.ip_list

if __name__ == '__main__':
    s = Source()
    s.get_list()
