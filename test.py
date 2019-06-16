import os
from scripts.log import Logger
from scripts.statistics import time_length, iteration_length, iteration_time


def test_statistic():
    LOGGER = Logger('logs')
    LOGGER.load_log()

    files = []

    file_name = 'time_length.png'
    file_path = os.path.abspath('static\\'+file_name)
    time_length(LOGGER.log, file_path)
    files.append('/static/' + file_name)

    file_name = 'iteration_length.png'
    file_path = os.path.abspath('static\\'+file_name)
    iteration_length(LOGGER.log, file_path)
    files.append('/static/' + file_name)

    file_name = 'iteration_time.png'
    file_path = os.path.abspath('static\\'+file_name)
    iteration_time(LOGGER.log, file_path)
    files.append('/static/' + file_name)


test_statistic()
