import time
from scripts.data import read_csv, write_csv
from datetime import datetime
import os
from glob import glob


class Logger:
    def __init__(self, log_dir=''):
        self.log = []
        self.log_dir = os.path.abspath(log_dir)

    def __del__(self):
        self.save_log()

    def add_info(self, info):
        self.log.append(info)

    def save_log(self):
        file_name = 'log{}.csv'.format(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S"))
        file_path = os.path.join(self.log_dir, file_name)
        write_csv(file_path, self.log)
        return file_name

    def load_log(self, path=None):
        self.log = []
        if not path:
            list_of_files = glob(self.log_dir + '\\*.csv')
            if list_of_files:
                path = max(list_of_files, key=os.path.getctime)
        if path:
            self.log = read_csv(path)
