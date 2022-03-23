import matplotlib.pyplot as plt
import seaborn as sns


def poisson():
    a = []
    f = open("local_poisson_n1000_l2.txt")
    for line in f.readlines():
        if line.strip()!="":
            a.append(float(line))
    f.close()
    a.append(8)
    a.append(10)
    ax = sns.countplot(a, color="dodgerblue")
    sns.lineplot(x=[0,0.25,0.5,1,1.5,2,3,4,5,6,7,8,9,10], y=[1300,2250,2500,2650,2800,2750,1750,1000,450,150,50,20, 15, 5], ax=ax, color="r")
    ax.set_yticks([])
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_xlabel("")
    plt.show()


def normal():

    a = []
    f = open("local_normal_n10000.txt")
    for line in f.readlines():
        if line.strip()!="":
            a.append(float(line))
    f.close()
    ax = sns.distplot(a, bins=15, kde=True, rug=False, hist=True, color="r", hist_kws={"color": "dodgerblue",
                                                                                       'edgecolor': 'black',
                                                                                       "linewidth": 2})
    ax.set_yticks([])
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_xlabel("")
    plt.show()


def noise():
    a = []
    f = open("local_normal_n1000_noisy.txt")
    for line in f.readlines():
        if line.strip()!="":
            a.append(float(line))
    f.close()
    ax = sns.distplot(a, kde=True, rug=False, hist=True, color="r", hist_kws={"color": "dodgerblue",
                                                                                       'edgecolor': 'black',
                                                                                       "linewidth": 2})
    ax.set_yticks([])
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_xlabel("")
    plt.show()


def noise_scatter():
    anscombe = sns.load_dataset("anscombe")
    ax = sns.lmplot(x="x", y="y", data=anscombe.query("dataset == 'III'"),
               ci=None, scatter_kws={"s": 80});
    plt.show()
