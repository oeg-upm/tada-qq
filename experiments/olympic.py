import os
import logging
from datetime import datetime
from experiments import common
from experiments.common import annotate_file, eval_column, compute_scores
import pandas as pd
from pandas.api.types import is_numeric_dtype
from easysparql import easysparql

from qq.qqe import QQE
from qq.dist import get_data
from experiments.common import uri_to_fname, create_dir

SHOW_LOGS = False

data_dir = "local_data"
# data_dir = "../local_data"

# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_olympic_games(endpoint, remove_outliers, meta_dir, err_meth, estimate):
    """
    endpoint:
    remove_outliers:
    meta_dir:
    """
    olympic_games_dir = 'olympic_games'
    olympic_games_data_dir = os.path.join(data_dir, olympic_games_dir, 'data')
    f = open(meta_dir)
    eval_data = []
    for line in f.readlines():
        atts = line.split(',')
        if len(atts) > 1:
            fname = atts[0].strip()
            class_uri = atts[1].strip()
            col_id = int(atts[2])
            uris = atts[3].split(';')
            trans_uris = [uri_to_fname(uri) for uri in uris]
            fdir = os.path.join(olympic_games_data_dir, fname)
            if SHOW_LOGS:
                print("fdir: ")
                print(fdir)
            preds = annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint,
                                  data_dir=data_dir, min_objs=MIN_NUM_OBJ, cols=[col_id], err_meth=err_meth,
                                  estimate=estimate)
            for c in preds:
                res = eval_column(preds[c], correct_uris=trans_uris, fdir=fdir, col_id=col_id)
                eval_data.append(res)
                if not res:
                    if SHOW_LOGS:
                        print(preds)

    prec, rec, f1 = compute_scores(eval_data, k=1)
    if SHOW_LOGS:
        print("\nresults: ")
        print(eval_data)
        print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))
    return prec, rec, f1


if __name__ == '__main__':
    a = datetime.now()
    common.PRINT_DIFF = SHOW_LOGS
    print("\n\n| %15s | %9s | %15s | %9s | %9s | %5s |" % (
    "remove outlier", "estimate", "error method", "Precision", "Recall", "F1"))
    print("|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 9, "-" * 9, "-" * 5))
    for ro in [True, False]:
        ro_txt = str(ro)
        for est in [True, False]:
            if est:
                est_txt = "estimate"
            else:
                est_txt = "exact"
            for err_meth in ["mean_err", "mean_sq_err", "mean_sqroot_err"]:
                prec, rec, f1 = annotate_olympic_games(endpoint='https://en-dbpedia.oeg.fi.upm.es/sparql',
                                                       remove_outliers=ro,
                                                       meta_dir="experiments/olympic_meta.csv", estimate=est,
                                                       err_meth=err_meth)
                print("| %15s | %9s | %15s | %9.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, err_meth, prec, rec, f1))

    b = datetime.now()

    print("\n\nTime it took: %f.1 seconds\n\n" % (b - a).total_seconds())
    # print(b - a)
    # print("")
    # print((b - a).total_seconds() / 60.0)
