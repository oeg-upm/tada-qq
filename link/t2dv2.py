import argparse
import os
from collections import Counter
from datetime import datetime
import pandas as pd
from qq.qqe import QQE
from experiments.common import is_numeric_dtype, uri_to_fname

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')

SAVE_MEMORY = False


def get_col(fname, colid):
    fpath = os.path.join(data_dir, fname)
    df = pd.read_csv(fpath, thousands=',')
    col = df[df.columns[int(colid)]]

    if not is_numeric_dtype(col):
        col = col.str.replace(',', '').astype(float, errors='ignore')
    col = pd.to_numeric(col, errors='coerce')
    col = col[~col.isnull()]

    return col


def column_group_matching(groups, ele, fetch_method, err_meth, err_cutoff):
    """
    Add column to one of the groups (or to a new group)
    """
    min_idx = None
    min_err = 1
    # print("ele col")
    # print(list(ele["col"]))
    qq = QQE(list(ele["col"]))
    # print("groups: ")
    # print(groups)
    for idx, g in enumerate(groups):
        if g:
            print("group-> ")
        else:
            print("group None")
            raise Exception("group is None")
        # print(g)
        top_ele = g[0]
        if top_ele is None:
            raise Exception("top_ele is None")
        # print("top ele:")
        # print(top_ele)
        err = qq.predict_and_get_error(top_ele["col"], method=err_meth, remove_outliers=False)
        if err < min_err:
            min_idx = idx
            min_err = err

    if min_err < err_cutoff:
        # print("cut off")
        group = add_col_to_group(ele, groups[min_idx], fetch_method)
        # print(group)
        groups[min_idx] = group
    else:
        # print("new group")
        groups.append([ele])
    if groups[-1] is None:
        print(ele)
        raise Exception("Boo")


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


def get_class_property_groups(df):
    d = dict()
    counts = []
    for idx, row in df.iterrows():
        c = row["concept"]
        ps = row["property"].split(';')
        prev_identified = None
        v = "%d-%s-%s" % (idx, c, uri_to_fname(ps[0]))
        for p in ps:
            k = c + " " + p
            if k in d:
                prev_identified = d[k]
                break
            d[k] = v

        if prev_identified:
            print("picking a prev-identified\t%s\t%d" % (prev_identified, idx))
            v = prev_identified
            for p in ps:
                k = c + " " + p
                d[k] = prev_identified
        counts.append(v)
    return d, Counter(counts)


def evaluate(groups, counts):
    """
    groups: [ [{}], [{}]]
    """
    scores = dict()
    for g in groups:
        cluses = [ele['gs_clus'] for ele in g]
        c = Counter(cluses)
        clus = c.keys()[0]
        scores[clus]


def workflow(fetch_method, err_meth, err_cutoff):
    df = pd.read_csv(meta_dir)
    df = df[df.property.notnull()]
    df = df[df["concept"].notnull()]
    df = df[df["pconcept"].notnull()]
    df = df[df["loose"] != "yes"]
    cp_groups, counts = get_class_property_groups(df)
    # fetch_method = "max"
    groups = []
    for idx, row_and_i in enumerate(df.iterrows()):
        i, row = row_and_i
        # if idx >= 15:
        #     break
        # print(row)
        col = get_col(fname=row['filename']+".csv", colid=row['columnid'])
        ele = {
            'col_id': row['columnid'],
            'fname': row['filename'],
            'col': col,
            'num': len(col),
            'concept': row['concept'],
            'property': row['property'].split(';')[0]
        }

        column_group_matching(groups, ele, fetch_method, err_meth, err_cutoff)
        # if idx >= 7:
        #     print("col %d: " % idx)
        #     print(ele)
        #     print("groups: ")
        #     print(groups[-1])

    for idx, g in enumerate(groups):
        print("\n\nGroup %d" % idx)
        print("===========")
        for ele in g:
            k = ele['concept']+" "+ele['property']
            ele['gs_clus'] = cp_groups[k]
            print("%s\t%s" % (ele['fname'], ele['gs_clus']))


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')

    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+",
                        help="Functions to computer errors.")
    parser.add_argument('-c', '--cutoff', default=0.1,
                        help="Error cutoff value.")
    args = parser.parse_args()
    return args.err_meths, float(args.cutoff)


if __name__ == '__main__':
    a = datetime.now()
    err_meths, cutoff = parse_arguments()
    for err_m in err_meths:
        workflow(fetch_method="max", err_meth=err_m, err_cutoff=cutoff)
    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

