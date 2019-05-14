import pandas as pd


def get_plt(df, file_path, x, y, x_label, y_label, title):
    import matplotlib.pyplot as plt

    plt.style.use('seaborn-pastel')
    # fig = Figure()
    # ax = fig.add_subplot(111)
    ax = plt.gca()
    plt.plot(x, y, label='данные из файла', marker='o', linewidth=4, markersize=12)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    ax.set_xscale('log')
    # fig, ax = plt.subplots()
    # ax.scatter(x, y)
    # for i, txt in enumerate(list(df['input'])):
    #     ax.annotate(txt, (x[i], y[i]))
    # plt.show()
    # return plt  # .show()
    # fig.autofmt_xdate()
    # canvas = FigureCanvas(plt)
    # png_output = BytesIO()
    # canvas.print_png(png_output)
    plt.savefig(file_path)
    plt.cla()
    # return png_output


def time_length(log, file_path):
    if log:
        df = pd.DataFrame(log)

        x_name = 'execution_time'
        y_name = 'length'
        x = list(map(lambda x: float(x), list(df[x_name])))
        y = list(map(lambda x: float(x), list(df[y_name])))

        return get_plt(df=df, x=x, y=y, file_path=file_path,
                       x_label='Время выполнения алгоритма', y_label='Количество полученных результатов',
                       title='Зависимость количества результатов от времени выполнения')
    else:
        return 'Лог пуст'


def iteration_length(log, file_path):
    if log:
        df = pd.DataFrame(log)
        x_name = 'iteration'
        y_name = 'execution_time'
        x = list(map(lambda x: int(x), list(df[x_name])))
        y = list(map(lambda x: float(x), list(df[y_name])))

        return get_plt(df=df, x=x, y=y, file_path=file_path,
                       x_label='Номер итерации', y_label='Время выполнения алгоритма',
                       title='Зависимость количества результатов от количества итераций')
    else:
        return 'Лог пуст'


def get_df(log):
    return pd.DataFrame(log)


