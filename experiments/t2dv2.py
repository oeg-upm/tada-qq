from datetime import datetime
import os

import numpy as np

from experiments.common import annotate_file, eval_column, compute_scores, uri_to_fname, compute_scores_per_property
import pandas as pd

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')
# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_t2dv2(endpoint, remove_outliers):
    """
    endpoint:
    remove_outliers: bool
    filename,concept,k,column,property,columnid,kind,sub_kind
    """
    eval_data = []
    df = pd.read_csv(meta_dir)
    df = df[df.property.notnull()]
    df = df[df["concept"].notnull()]
    df = df[df["pconcept"].notnull()]

    eval_per_prop = dict()
    for idx, row in df.iterrows():
        class_uri = 'http://dbpedia.org/ontology/'+row['concept']
        col_id = int(row['columnid'])
        uris = row['property'].split(';')
        trans_uris = [uri_to_fname(uri) for uri in uris]
        csv_fname = row['filename']+".csv"
        fdir = os.path.join(data_dir, csv_fname)
        preds = annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint,
                              data_dir="local_data", min_objs=MIN_NUM_OBJ, cols=[col_id])
        pconcept = row['pconcept']
        if pconcept in [None, np.nan, np.NaN]:
            print("is none")
            print(row)
        if pconcept not in eval_per_prop:
            eval_per_prop[pconcept] = []

        diff_name = "%s-%s-%s" % (uri_to_fname(class_uri), uri_to_fname(uris[0]), fdir.split(os.sep)[-1])

        for c in preds:
            res = eval_column(preds[c], correct_uris=trans_uris, class_uri=class_uri, col_id=col_id, fdir=fdir,
                              diff_diagram=os.path.join("experiments", "diffs", "t2dv2", diff_name))
            eval_data.append(res)
            eval_per_prop[pconcept].append(res)

    prec, rec, f1 = compute_scores(eval_data, k=1)
    print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))
    compute_scores_per_property(eval_per_prop, "t2dv2")


if __name__ == '__main__':
    a = datetime.now()
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=True)
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

