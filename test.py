import os
import json
from scripts.data import load_trie, load_pickle, get_path_above
from scripts.database import DataBase
from scripts.log import Logger
from scripts.key import search
from scripts.statistics import time_length, iteration_time, iteration_length
from scripts.data import transform_dict, json_load, json_dump


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


def test_performance(test_list, dict_limit):
    FULL_OLD_DICT = load_pickle(get_path_above('resources/full_dict.pickle'))
    SYNONYMIZER = load_pickle(get_path_above('resources/synonymizer.pickle'))
    TRIE = load_trie(get_path_above('resources/corpus.trie'))
    TRIE_SLANG = load_trie(get_path_above('resources/slang.trie'))
    LOGGER = Logger('logs')

    FULL_DICT = {}
    i = 0
    step = round(200000/dict_limit)

    for el in FULL_OLD_DICT["test_dict"]:
        i += 1
        if i != step:
            continue
        else:
            i = 0
            FULL_DICT[el] = FULL_OLD_DICT["test_dict"][el]
    FULL_DICT = transform_dict(FULL_DICT)

    for el in test_list:
        res, info = search(el, FULL_DICT, SYNONYMIZER, TRIE, TRIE_SLANG)
        LOGGER.add_info(info)

    LOGGER.save_log(dict_limit)


test_performance(json_load("test\\test_list.json"), 50000)
test_performance(json_load("test\\test_list.json"), 100000)
test_performance(json_load("test\\test_list.json"), 200000)
