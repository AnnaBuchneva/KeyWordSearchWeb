import functools
import re
from math import log


PREFIXES_FREQ_DICT = {}
DELTAS = [0.05, 0.25, 0.1, 0.2, 0.2, 0.05, 0.15]
STW = 0.34
STD = 0.19
NW = 0.36


def split_by_list(string, begins, par=0):
    """
    "Making words" from begins list of indexes of word beginnings

    :param string: example 'noway'
    :param begins: [int,int,int...]
    :param par: if deb par = 1
    :return: 'no way'
    """

    word_list = []
    if begins:
        for i in range(len(begins)):
            if i == len(begins) - 1:  # if 'i' is last index
                word_list.append(string[begins[i] - 1:])
            else:
                word_list.append(string[begins[i] - 1: begins[i + 1] - 1])
    if par == 0:
        return ' '.join(word_list)
    if par == 1:
        return word_list


def split_hashtag_by_digits(hashtag_wo_sharp):
    re_result = re.split('(\d+)', hashtag_wo_sharp)
    wordpart = ''
    digitpart = ''
    for i, part in enumerate(re_result):
        if part.isdigit():
            digitpart = (part, i)
        elif part:
            wordpart = (part, i)
    if not digitpart:
        digitpart = ('', 0)
    if not wordpart:
        wordpart = ('', 0)
    return (wordpart, digitpart)


def split_by_underscore(hashtag_wo_sharp):
    if len(hashtag_wo_sharp.split('_')) > 1:
        result = ' '.join(hashtag_wo_sharp.split('_'))
        result = result.rstrip()
        return result
    else:
        return None


# @functools.lru_cache(maxsize=None)
def get_prefixes_freq(hashtag, TRIE, TRIE_SLANG):  # looking for data in our prefix trie
    for letter in range(0, len(hashtag) + 1):
        prefixes = TRIE.prefix_items(hashtag[letter:]) + TRIE_SLANG.prefix_items(hashtag[letter:])
        for prefix in prefixes:
            global PREFIXES_FREQ_DICT
            PREFIXES_FREQ_DICT[prefix[0]] = prefix[1]  # {'prefix1': ln(match_count1),'prefix2': ln(match_count2)}


@functools.lru_cache(maxsize=None)
def recursive_algorithm(int_arg, hashtag_wo_sharp, scoring_function):  # int_arg = 2 (example)
    """
    Main recursive algorithm function V(i) from 2.5

    :param int_arg: len of our hashtag
    :param hashtag_wo_sharp: 'hashtag'
    :return: result of recursive formula from 2.5 Inference Algorithms 'Segmenting Web-Domains and Hashtags using
    Length Specific Models'  [score, [wbegin1,wbegin2...]]
    """

    if int_arg == 0:
        v_score = (0, [])
        return v_score  # need empty list for zero arg result, later iterate from 1 may be
    begin = len(hashtag_wo_sharp) - (int_arg - 1)  # 5 - ((int_arg=2)-1) = 4
    v_list = []  # list to check max score
    for slice in range(int_arg):  # 0,1 ::if int_arg=2
        beginnings = []  # list of all begin letters of word (in the end contains only maxed by score of V beginnings)
        end = len(hashtag_wo_sharp) - slice  # 1: end = 5 2: end = 4  => pass1: f(4,5) pass2: f(4,4) (int_arg =2)
        v_prev = recursive_algorithm(slice, hashtag_wo_sharp,
                                     scoring_function)  # previous result of function getting from cache
        v_score = scoring_function(begin, end, hashtag_wo_sharp) + v_prev[0]
        beginnings.append(begin)  # new word begin index
        beginnings = beginnings + v_prev[1]  # getting previous beginnings
        v_list.append([v_score, beginnings])
    return max(v_list)


@functools.lru_cache(maxsize=None)
def viterbi_seg_score(begin, end, hashtag, prefixes_freq_dict=PREFIXES_FREQ_DICT, deb=0):
    """
    Scoring function
    Use with recursive_algorithm
    :param begin: begin of our word
    :param end: end of our word
    :param hashtag: split of our hashtag
    :param prefixes_freq_dict: {'prefix1': ln(match_count1),'prefix2': ln(match_count2), ...}
    :param deb - debugging
    :return: if in dict: log(Prob_unigramm) else -100  , OOV : len(hashtag_split)
    """

    if deb == 0:
        hashtag_split = hashtag[begin - 1:end]
    else:
        hashtag_split = hashtag

    if hashtag_split in prefixes_freq_dict and prefixes_freq_dict[hashtag_split] != 0:
        score = prefixes_freq_dict[hashtag_split] # check if in {'prefix1': match_count1,'prefix2': match_count2, ...}
        return log(score)
    else:
        return -2000000000


def segment(hashtag, TRIE, TRIE_SLANG,
            scoring_function=viterbi_seg_score,
            recursive_algorithm=recursive_algorithm):

    hashtag_wo_sharp = hashtag.lower().strip()
    re_result = split_hashtag_by_digits(hashtag_wo_sharp)
    underscore = split_by_underscore(hashtag_wo_sharp)
    if underscore:
        total_result = ' '.join(hashtag_wo_sharp.split('_'))
        total_result = total_result.rstrip()
    else:
        get_prefixes_freq(hashtag_wo_sharp, TRIE, TRIE_SLANG)
        result_in_digits = recursive_algorithm(len(re_result[0][0]), re_result[0][0], scoring_function)
        result_in_words = split_by_list(re_result[0][0], result_in_digits[1]).rstrip()
        if re_result[1][1] > re_result[0][1]:
            result_in_words = result_in_words + ' ' + re_result[1][0]
        else:
            result_in_words = re_result[1][0] + ' ' + result_in_words
        total_result = result_in_words.strip()

    return total_result
