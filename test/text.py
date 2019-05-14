import pickle
def dump_pickle(obj, path):
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def load_pickle(file_path):
    with open(file_path, "rb") as file:
        return pickle.load(file)

def reload():
    synonim = load_pickle('resources/synonymizer_new.pickle')
    new_symomin = {}
    counter = 0
    for el in synonim:
        counter += 1
        new_symomin[el] = synonim[el]
        if counter>270000:
            break
    dump_pickle(new_symomin, 'resources/synonymizer_new.pickle')

reload()
