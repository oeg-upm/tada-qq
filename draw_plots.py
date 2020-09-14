from easysparql import easysparql
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns


def remove_outliers(sample):
    column = sample
    if len(column) < 1:
        return []
    clean_column = []
    q1 = np.percentile(column, 25)
    q3 = np.percentile(column, 75)
    # k = 1.5
    k = 2
    # [Q1 - k(Q3 - Q1), Q3 + k(Q3 - Q1)]
    lower_bound = q1 - k * (q3 - q1)
    upper_bound = q3 + k * (q3 - q1)
    for c in column:
        if c >= lower_bound and c <= upper_bound:
            clean_column.append(c)
    return clean_column


def get_column(fdir, colid):
    """
    :param fdir:
    :param colid:
    :return: a list of the cells of the colid
    """
    print("open: "+fdir)
    df = pd.read_csv(fdir)
    df = df[df.iloc[:, colid].notnull()]
    col = list(df.iloc[:, colid])
    # col = list(df[df.columns[colid]])
    return col


def histogram(x):
    sns.set()
    # penguins = sns.load_dataset("penguins")
    # a = penguins['flipper_length_mm']
    # b = list(a)
    b = x
    # Sample
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="r", hist_kws={'cumulative': True, 'density': True, 'range': (150, 220)})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="r", hist_kws={'cumulative': True, 'range': (150, 220)})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="r", hist_kws={'cumulative': True, 'range': (120,240)})
    # CDF
    sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="b", hist_kws={'cumulative': True, 'density': True, 'range': (150, 220)})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="b", hist_kws={'cumulative': True, 'range': (150, 220)})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="b", hist_kws={'cumulative': True})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, color="r", hist_kws={'cumulative': True})
    # PDF
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=200, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=500, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=150, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=80, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=60, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=50, hist_kws={'cumulative': False})
    #sns.distplot(b, hist=True, kde=False, rug=False, bins=40, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=30, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=20, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=15, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=10, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=5, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, rug=False, bins=2, hist_kws={'cumulative': False})
    # sns.distplot(b, hist=True, kde=False, hist_kws={'cumulative': True})
    # print(b)
    # np.random.seed(0)
    # x = np.random.randn(100)
    # ax = sns.distplot(x)
    # print(x)
    # print(len(x))
    # x = pd.Series(x, name="x variable")
    # ax = sns.distplot(x)
    # ax.show()
    # df = pd.DataFrame([x], headers=['x'])
    # print(df)
    # ax = sns.distplot(df[], hist=True, kde=False)


    # ax = sns.distplot(x, hist=True, kde=False, rug=True)
    #
    # ax = sns.distplot(x, bins=15, kde=False, rug=False, hist=True, color="r", hist_kws={"color": "dodgerblue",
    #                                                                                    'edgecolor': 'black',
    #                                                                                    "linewidth": 2})

    # ax = sns.displot(x, kind="hist")
    # df = pd.DataFrame(zip(x,y), columns=["x","y"])
    # print(df)
    # sns.lmplot(x="x", y="y", data=df)
    # ax = sns.scatterplot(x="x", y="y", data=df, linewidth=0.05)
    # ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([0,1],[0,1]), columns=["x","y"]), ax=ax)
    # plt.savefig('fig.eps', format='eps')
    plt.savefig('fig-sample-cdf-1.png', format='png')
    plt.show()


# def histogram(x):
#     import pandas as pd
#     import matplotlib
#     matplotlib.use('TkAgg')
#     import matplotlib.pyplot as plt
#     import seaborn as sns
#     df = pd.DataFrame(zip(x,y), columns=["x","y"])
#     # print(df)
#     # sns.lmplot(x="x", y="y", data=df)
#     ax = sns.scatterplot(x="x", y="y", data=df, linewidth=0.05)
#     ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([0,1],[0,1]), columns=["x","y"]), ax=ax)
#     # plt.savefig('fig.eps', format='eps')
#     plt.show()

def get_col_data(fdir):
    col = get_column(fdir, 0)
    num_col = easysparql.get_numerics_from_list(col, 0)
    return num_col


def get_col_data_sample():
    colid = 1
    a = 'local_data/olympic_games/data/aaaboxers.csv'
    df = pd.read_csv(a)
    print("df: ")
    print(df)
    df = df[df.iloc[:, colid].notnull()]
    col = list(df.iloc[:, colid])
    return col

# a = 'local_data/dbo-BasketballPlayer/dbo-Person-height.txt'
# a = 'local_data/dbo-BasketballPlayer/dbp-heightCm.txt'
# a = 'local_data/dbo-Boxer/dbo-height.txt'
# a = 'local_data/dbo-Boxer/dbo-Person-height.txt'
# a = 'local_data/dbo-Boxer/dbo-Person-height.txt'
# for the property one
a = 'local_data/dbo-Boxer/dbp-height.txt'
height = get_col_data(a)
# for the column
# height = get_col_data_sample()
height = list(set(height))
height = remove_outliers(height)
print(len(height))
histogram(height)
