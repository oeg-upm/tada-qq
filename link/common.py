from collections import Counter
import pandas as pd
import seaborn as sns
from qq.qqe import QQE
import matplotlib.pyplot as plt

import os

SAVE_MEMORY = False


def add_col_to_group(ele, group, fetch_method):
    """
    Add ele to group.
    """
    if fetch_method == "max":
        if group[0]["num"] < ele["num"]:
            group.append(group[0])
            if SAVE_MEMORY:
                group[-1]["col"] = []
            group[0] = ele
        else:
            if SAVE_MEMORY:
                ele["col"] = []
            group.append(ele)
    elif fetch_method == "min":
        if group[0]["num"] > ele["num"]:
            group.append(group[0])
            group[-1]["col"] = []
            group[0] = ele
        else:
            if SAVE_MEMORY:
                ele["col"] = []
            group.append(ele)
    else:
        raise Exception("unknown fetch method")
    return group


def column_group_matching(groups, ele, fetch_method, err_meth, err_cutoff):
    """
    Add column to one of the groups (or to a new group)
    """
    min_idx = None
    min_err = 1
    qq = QQE(list(ele["col"]))
    for idx, g in enumerate(groups):
        if not g:
            print("group None")
            raise Exception("group is None")
        top_ele = g[0]
        if top_ele is None:
            raise Exception("top_ele is None")
        err = qq.predict_and_get_error(top_ele["col"], method=err_meth, remove_outliers=False)
        if err < min_err:
            min_idx = idx
            min_err = err

    if min_err < err_cutoff:
        group = add_col_to_group(ele, groups[min_idx], fetch_method)
        groups[min_idx] = group
    else:
        groups.append([ele])
    if groups[-1] is None:
        print(ele)
        raise Exception("Boo")


def evaluate(groups, counts):
    """
    groups: [ [{}], [{}]]
    counts: Counter of cluster values. Each value = "idx-concept-shot_property"
    """
    print("\n\nEVALUATE\n==============\n")
    max_per_v = dict()
    for idx, g in enumerate(groups):
        vals = [ele['gs_clus'] for ele in g]
        c = Counter(vals)
        for k in c:
            prec = c[k] / len(vals)
            if k in max_per_v:
                if (c[k] > max_per_v[k]['num']) or (c[k] == max_per_v[k]['num'] and prec > max_per_v[k]['prec']):
                    max_per_v[k] = {
                        'num': c[k],
                        'prec': prec,
                        'clus_id': idx
                    }
            else:
                max_per_v[k] = {
                    'num': c[k],
                    'prec': prec,
                    'clus_id': idx
                }

    scores = dict()
    precs = []
    recs = []
    f1s = []
    print("{:<35} {:<5} {:<5} {:<5} {:<5}".format("name", "prec", "rec", "f1", "clus"))
    for k in max_per_v:
        prec = max_per_v[k]['prec']
        rec = max_per_v[k]['num'] / counts[k]
        f1 = 2 * prec * rec / (prec + rec)
        scores[k] = {'prec': prec, 'rec': rec, 'f1': f1}
        precs.append(prec)
        recs.append(rec)
        f1s.append(f1)
        print("{:<35} {:<5} {:<5} {:<5} {:<5}".format(k, round(prec, 3), round(rec, 3), round(f1, 3), max_per_v[k]['clus_id']))
    p, r, f = sum(precs)/len(precs), sum(recs)/len(recs), sum(f1s)/len(f1s)
    print("Average: Precision (%.3f), Recall (%.3f), F1 (%.3f)" % (p, r, f))
    return p, r, f


def generate_clus_diagram(scores):
    """
    :param scores: dict
    :return: None
    """
    rows = []
    scores_titles = ["Precision", "Recall", "F1"]
    for k in scores:
        for idx, sc in enumerate(scores_titles):
            row = [str(k), scores[k][idx], scores_titles[idx]]
            rows.append(row)
        # row = [k, scores[k][0], scores[k][1], scores[k][2]]
        # rows.append(row)
    df = pd.DataFrame(rows, columns=['Cutoff', 'Score', 'Metric'])
    df['Cutoff'] = df['Cutoff'].astype('category')
    linestyles = ["--", ":", "dashdot"]
    ax = sns.lineplot(x="Cutoff", y="Score",
                     hue="Metric",
                     data=df, linewidth=2, style="Metric",
                     # palette="colorblind",
                     # palette="Spectral",
                     # palette="pastel",
                     # palette="ch:start=.2,rot=-.3",
                     # palette="YlOrBr",
                     # palette="Paired",
                     # palette="Set2",
                     # orient="h"
                      )

    ax.legend(loc=2, fontsize='x-small')
    ax.figure.savefig('%s.svg' % os.path.join('results', 'clustering', 't2dv2'), bbox_inches="tight")
    # plt.show()
    # ax.figure.clf()
