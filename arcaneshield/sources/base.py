from tqdm import tqdm, trange

class BaseSource(object):
    name = 'BaseSource'

    def __init__(self):
        self.ip_list = []

    def set_pbar(self, pbar):
        self.pbar = pbar

    def get_length(self):
        raise NotImplemented

    def get_list(self):
        raise NotImplemented
