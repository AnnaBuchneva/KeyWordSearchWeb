from pymorphy2 import MorphAnalyzer
import re


# Объект для нормализации слов
morph = MorphAnalyzer()

# Длина n-грамм
n_gramm_value = 3

# Максимально допустимое расстояние Дамерау-Левенштайна
maxDistanceInReplaceCheck = 1

# Вероятность для найденных слов нечетким поиском по расстоянию Дамерау-Левенштайна
probabilityForFoundWordsInReplace = 1

# Стоимость удаления символа
damerauDeleteCost = 1

# Стоимость вставки символа
damerauInsertCost = 1

# Стоимость замены символа
damerauReplaceCost = 1

# Стоимость перестановки символов
damerauTransposeCost = 1


def normalize_hashtag(hashtag):
    """
    Обработка вводимого хэштега, чтобы в нем остались только буквы
    Необходимо чтобы все хэштеги были в одной форме и их удобно было сравнивать между собой

    :param hashtag: вводимый хэштег
    :return: обработанный хэштег
    """

    result = "".join(re.findall(r"\w*", hashtag)).lower()
    return result


def normalize_word(word):
    """
    Получение нормальной формы слова (например гуляла -> гулять)

    :param word: слово
    :return: нормальная форма слова
    """

    result = morph.parse(word)[0].normal_form.lower()
    return result


def lemm_list(split_str):
    """
    Получение списка нормализованных слов из списка слов

    :param split_str: список слов
    :return: список нормализованных слов
    """

    lemm_list = []
    for el in split_str:
        lemm_list.append(normalize_word(el))
    return lemm_list


def make_n_gramms(input_str):
    """
    Получение n-грамм из строки

    :param input_str: строка
    :return: список n-грамм
    """

    result = []
    for i in range(n_gramm_value, len(input_str) + 1):
        result.append(input_str[i - n_gramm_value: i])

    return result


def get_words(hashtag):
    """
    Разбивает строку на слова по пробелам, предварительно удаляя решетку

    :param hashtag: строка ввода
    :return: список слов
    """

    hashtag = hashtag.replace("#", "")

    return hashtag.split(" ")


def damerau(s, t):
    """
    Подсчет расстояния Дамерау-Левенштейна (расстояние с перестановкой)

    :param s: строка 1
    :param t: строка 2
    :return: расстояние между строками
    """

    if s == t:
        return 0
    elif len(s) == 0:
        return len(t)
    elif len(t) == 0:
        return len(s)

    deleteCost = damerauDeleteCost
    insertCost = damerauInsertCost
    replaceCost = damerauReplaceCost
    transposeCost = damerauTransposeCost

    s = " " + s
    t = " " + t
    M = len(s)
    N = len(t)
    d = [list(range(N))]
    for i in range(1, M):
        d.append([])
        for j in range(N):
            d[i].append(0)
        d[i][0] = i

    for i in range(1, M):
        for j in range(1, N):
            # Стоимость замены
            if s[i] == t[j]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = d[i - 1][j - 1] + replaceCost
            d[i][j] = min(
                d[i][j],  # замена
                d[i - 1][j] + deleteCost,  # удаление
                d[i][j - 1] + insertCost  # вставка
            )

            if i > 1 and j > 1 and s[i] == t[j - 1] and s[i - 1] == t[j]:
                d[i][j] = min(
                    d[i][j],
                    d[i - 2][j - 2] + transposeCost  # транспозиция
                )
    return d[M - 1][N - 1]


def get_result_by_damerau(word, dict_word):
    """
    Линейный нечеткий поиск слова по словарю с использованием расстояния Дамерау-Левенштейна

    :param word: искомое слово
    :param dict_word: словарь, по которому выполняется поиск
    :return: расстояние между строками
    """

    gramms_selection = {}
    for el in dict_word:
        for w in word:
            len = damerau(el, w)
            if len < 2:
                gramms_selection[w] = (2 - len) * 0.5

    return gramms_selection
