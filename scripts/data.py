import pickle
import csv
import os
import datrie
import json
from scripts.grammar import make_n_gramms, lemm_list, normalize_hashtag, get_words


def load_trie(file_path):
    return datrie.Trie.load(file_path)


def dump_pickle(obj, path):
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def load_pickle(file_path):
    with open(file_path, "rb") as file:
        return pickle.load(file)


def get_path_above(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', path))


def read_csv(path):
    with open(path, newline='', encoding="utf-8-sig") as csv_file:
        result = []
        lines = csv.DictReader(csv_file, delimiter=';', quotechar='|')
        for line in lines:
            result.append(dict(line))
        return result


def write_csv(path, obj):
    csv_columns = obj[0].keys()
    with open(path, mode='w', newline='', encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns, delimiter=';', quotechar='|')
        writer.writeheader()
        for data in obj:
            writer.writerow(data)


def read_dict(path):
    result = {}
    lines = read_csv(path)
    for line in lines:
        result[line["hashtag"]] = {"split": lemm_list(get_words(line["split"])),
                                   "count": int(line["count"]),
                                   "hashtag": line["hashtag"]}
    return result


def transform_dict(input_dict):
    result_words = {}
    result_hashtag = {}
    result_gramms_words = {}
    result_gramms_hashtag = {}

    for hashtag in input_dict:

        hashtag_value = normalize_hashtag(hashtag)
        result_hashtag[hashtag_value] = input_dict[hashtag]

        n_gramms_hashtag = make_n_gramms(hashtag_value)
        input_dict[hashtag]['n_gramms'] = n_gramms_hashtag
        for gramm in n_gramms_hashtag:
            if gramm not in result_gramms_hashtag:
                result_gramms_hashtag[gramm] = {}
            result_gramms_hashtag[gramm][hashtag_value] = input_dict[hashtag]

        for word in input_dict[hashtag]["split"]:
            if word not in result_words:
                result_words[word] = dict()
            result_words[word][hashtag_value] = input_dict[hashtag]

            n_gramms = make_n_gramms(word)
            for gramm in n_gramms:
                if gramm not in result_gramms_words:
                    result_gramms_words[gramm] = {}
                result_gramms_words[gramm][word] = {'n_gramms': n_gramms,
                                                    'res': result_words[word]}

    full_dict = {"test_dict": input_dict,
                 "words": result_words,
                 "hashtags": result_hashtag,
                 "gramms_words": result_gramms_words,
                 "gramms_hashtags": result_gramms_hashtag}

    return full_dict


def read_synonymizer(path):
    with open(path, "r", encoding="utf8") as file:
        lines = file.readlines()
    synonymizer = {}

    for line in lines:

        line = line.replace("\n", "")
        words = line.split("|")
        words = lemm_list(words)

        for word in words:
            word = word.strip().lower()

            if word not in synonymizer:
                synonymizer[word] = words

            if word not in synonymizer[word]:
                synonymizer[word].append(word)

    return synonymizer


def create_dict():
    synonymizer = read_synonymizer("synmaster.txt")

    dump_pickle(synonymizer, "synonymizer.pickle")

    test_dict = read_dict("test.csv")
    full_dict = transform_dict(test_dict)

    dump_pickle(full_dict, "full_dict.pickle")


def load_dict():
    with open(get_path_above("resourses\\full_dict.pickle"), "rb") as file:
        full_dict = pickle.load(file)
    with open(get_path_above("resourses\\synonymizer.pickle"), "rb") as file:
        synonymizer = pickle.load(file)
    return full_dict, synonymizer


def json_dump(path, something):
    json_text = "{}".format(json.dumps(something, ensure_ascii=False, indent=0))
    with open(path, "w", encoding="utf8") as file:
        file.write(json_text)


def json_load(path):
    with open(path, "r", encoding="utf8") as file:
        return json.loads(file.read())

