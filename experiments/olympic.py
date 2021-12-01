import os
import logging
from datetime import datetime

from experiments.common import annotate_file, eval_column, compute_scores
import pandas as pd
from pandas.api.types import is_numeric_dtype
from easysparql import easysparql

from qq.qqe import QQE
from qq.dist import get_data
from experiments.common import uri_to_fname, create_dir

data_dir = "local_data"
# data_dir = "../local_data"

# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_olympic_games(endpoint, remove_outliers, meta_dir):
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
            preds = annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint,
                          data_dir=data_dir, min_objs=MIN_NUM_OBJ, cols=[col_id])
            for c in preds:
                res = eval_column(preds[c], correct_uris=trans_uris)
                eval_data.append(res)
                if not res:
                    print(preds)
    print("\nresults: ")
    print(eval_data)
    prec, rec, f1 = compute_scores(eval_data, k=1)
    print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))


a = datetime.now()

annotate_olympic_games(endpoint='https://en-dbpedia.oeg.fi.upm.es/sparql', remove_outliers=True,
                       meta_dir="experiments/olympic_meta.csv")


b = datetime.now()

print("Time it took")
print(b-a)
print((b-a).total_seconds())
print((b-a).total_seconds()/60.0)

