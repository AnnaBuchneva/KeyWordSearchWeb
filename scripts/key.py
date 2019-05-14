import time
from datetime import datetime
from scripts.scoring import segment
from scripts.grammar import make_n_gramms, lemm_list, normalize_hashtag, get_words


# Коэффициент достоверности поиска по n-граммам
glob_gramms_acception = 0.7

# Коэффициент достоверности нечеткого поиска по словам
glob_words_acception = 0.6

# Минимальный возможный порог совпадения слов по n-граммам
min_gramms_acception = 0.5

# Минимальное количество возвращаемых хэштегов в результате
result_limit = 15

# Коэффициент достоверности нечеткого поиска по словам
glob_fuzzy_multiplier = 0.8

# Коэффициент достоверности поиска по синонимам
glob_synonyms_multiplier = 0.6

# Коэффициент достоверности нечеткого поиска по хэштегам
glob_fuzzy_hashtag_multiplier = 0.9


def preprosess_result(result, func=lambda x: x):
    """
    Предобработка результата нечеткого поиска хэштегов
    Ко всем полученным значениям применяется заданная функция

    :param result: результат
    :param func: функция, применяемая к результату
    :return: обработанный результат
    """

    return dict(map(lambda el: (el[0], func(el[1])), result.items()))


def get_synonims(list_words, synonymizer):
    """
    Получение синонимов для списка слов

    :param list_words: список слов
    :param synonymizer: словарь синонимов
    :return: список синонимов
    """

    result = []
    for word in list_words:
        result += synonymizer.get(word, [])
    return list(set(result))


def check_sack(word1, word2, two_side=True):
    """
    Проверка расстояния между двумя списками слов через мешок слов

    :param word1: список слов 1
    :param word2: список слов 2
    :param two_side: двухстороннее сравнение
    :return: расстояние между списками слов
    """

    diff = max(len(set(word1)-set(word2)), len(set(word2)-set(word1))) if two_side else\
        len(set(word1)-set(word2))
    return diff


def get_probability(value, length):
    return round((length-value)/length, 5)


def update_result(hashtags, *args):
    result = {}
    for sub_result in args:
        for element in sub_result:            
            result[element] = {'probability': round(max(result.get(element, {}).get('probability', 0),
                                                        sub_result.get(element, 0)),
                                                    5),
                               'frequency': hashtags[element]['count']}

    max_frequency = max([result[key]['frequency'] for key in result]) if result else 1
    for element in result:
        result[element]['total'] = round((0.7*result[element]['probability'])
                                         + (0.3*result[element]['frequency']/max_frequency), 5)
    return result


def update_all(*args):
    result = {}
    for sub_result in args:
        for element in sub_result:
            if (element in result and result[element]['total'] > sub_result[element]['total']) \
                    or element not in result:
                    result[element] = sub_result[element]

    return result


def get_subresult(gramms, dict_gramms, acceptation=0.5, n_key='n_gramms', multiplier=1.0, two_side=True):
    gramms_selection = {}
    
    for key in gramms:
        if dict_gramms.get(key):
            for word in dict_gramms[key]:      
                probability = get_probability(check_sack(dict_gramms[key][word][n_key], 
                                                         gramms, 
                                                         two_side=two_side),
                                              len(gramms))
                # if type(gramms) == dict:
                #     probability *= gramms[key]
                #
                if word not in gramms_selection:
                    gramms_selection[word] = probability
                # else:
                #     gramms_selection[word] = probability*0.5 + gramms_selection[word]*0.5
                    
    filter_result = {k: round(v*multiplier, 5) for k, v in gramms_selection.items() if v >= acceptation}
    
    return filter_result


def get_hashtag(word,
                split_words,
                full_dict,
                synonymizer,
                gramms_acception,
                words_acception,
                fuzzy_multiplier,
                synonyms_multiplier,
                fuzzy_hashtag_multiplier):

    g_word = make_n_gramms(word)
    
    list_words = lemm_list(split_words)
    # list_synonims = get_synonims(list_words, synonymizer)
    g_list_words = dict()

    # Точное совпадение целого хэштега
    accurate_hashtag = { word: 1 } if full_dict["hashtags"].get(word) else {}
    
    # Неточное совпадение целого хэштега
    fuzzy_hashtag = get_subresult(g_word, 
                                  full_dict["gramms_hashtags"],   
                                  acceptation=gramms_acception, 
                                  multiplier=fuzzy_hashtag_multiplier)

    # Точное попадание по словам
    accurate_words = get_subresult(list_words, 
                                   full_dict["words"], 
                                   acceptation=words_acception, 
                                   n_key="split")        

    # Неточное попадание по словам
    fuzzy_words = {}
    synonyms_words = []
    for i_word in list_words:  
        if synonymizer and synonymizer.get(i_word):
            synonyms_words += synonymizer.get(i_word)
        
        fuzzy_words[i_word] = 1
        g_list_words[i_word] = make_n_gramms(i_word)
        fuzzy_words.update(get_subresult(g_list_words[i_word], 
                                         full_dict['gramms_words'],   
                                         acceptation=gramms_acception))
        
    fuzzy_words = get_subresult(fuzzy_words, 
                                full_dict["words"],   
                                acceptation=words_acception,
                                multiplier=fuzzy_multiplier,
                                n_key="split",
                                two_side=False)
    
    synonyms_words = get_subresult(synonyms_words,
                                   full_dict["words"], 
                                   acceptation=words_acception,
                                   multiplier=synonyms_multiplier,
                                   n_key="split",
                                   two_side=False)
    
    result = update_result(full_dict["hashtags"],
                           accurate_hashtag, accurate_words, fuzzy_hashtag, fuzzy_words, synonyms_words)
    
    return result


def search(input_word, full_dict, synonymizer, trie, trie_slang):
    start_time = time.time()

    gramms_acception = glob_gramms_acception
    words_acception = glob_words_acception
    fuzzy_multiplier = glob_fuzzy_multiplier
    synonyms_multiplier = glob_synonyms_multiplier
    fuzzy_hashtag_multiplier = glob_fuzzy_hashtag_multiplier

    word = normalize_hashtag(input_word)
    split_words = get_words(segment(word, trie, trie_slang))

    res = []
    iteration = 0
    while (not res or len(res[-1]) < result_limit) and gramms_acception >= min_gramms_acception:
        iteration += 1

        res.append(get_hashtag(word,
                               split_words,
                               full_dict,
                               synonymizer,
                               gramms_acception,
                               words_acception,
                               fuzzy_multiplier,
                               synonyms_multiplier,
                               fuzzy_hashtag_multiplier))

        gramms_acception -= 0.1
        words_acception -= 0.1
        fuzzy_multiplier -= 0.1
        synonyms_multiplier -= 0.1
        fuzzy_hashtag_multiplier -= 0.1

    result = update_all(*res)
    result = sorted(result.items(), key=lambda x: x[1]['total'], reverse=True)

    info = {
        'time_mark': time.time(),
        'time': datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
        'input': input_word,
        'words': split_words,
        'length': len(result),
        'iteration': iteration,
        'execution_time': (time.time() - start_time)
    }

    print("--- input: {} "
          "--- words: {} "
          "--- result: {} "
          "--- iteration: {} "
          "--- time: {} ---".format(info['input'], info['words'],
                                    info['length'], info['iteration'], info['execution_time']))

    return result, info
