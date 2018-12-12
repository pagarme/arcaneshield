from sources import cloudproxies, gatherproxy, httptunnel, multiproxy, nordvpn, rebroproxy, samair, tor, xroxy
from threading import Thread, Lock
from queue import Queue
from tqdm import tqdm, trange
import os

def get_ip_list():

    s_list = [cloudproxies, gatherproxy, httptunnel, multiproxy, nordvpn, rebroproxy, tor]

    threads = []

    q = Queue()

    iplist = []

    i = 0
    for s in s_list:
        source = s.Source()

        source.set_pbar(tqdm(desc=source.name, total=source.get_length(), position=i, leave=False))

        t = Thread(target=source.get_list, args=(q, ))
        t.start()
        threads.append(t)
        i += 1

    for t in threads:
        t.join()

    while not q.empty():
        iplist += q.get()

    iplist = list(set(iplist))

    os.system('clear')

    print('[*] Got {} unique IPs'.format(len(iplist)))

    return iplist

if __name__ == '__main__':
    get_ip_list()
