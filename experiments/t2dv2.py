from datetime import datetime
import os
import argparse

import numpy as np

from experiments.common import annotate_file, eval_column, compute_scores, uri_to_fname, compute_scores_per_property
from experiments.common import get_num_rows, compute_counts
import pandas as pd

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')
# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_t2dv2(endpoint, remove_outliers, err_meth):
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
    folder_name = None

    test = True

    if err_meth == "mean_err":
        folder_name = "t2dv2-mean-err"
    elif err_meth == "mean_sq_err":
        folder_name = "t2dv2-mean-sq-err"
    files_k = dict()
    eval_per_prop = dict()
    for idx, row in df.iterrows():
        class_uri = 'http://dbpedia.org/ontology/'+row['concept']
        col_id = int(row['columnid'])
        uris = row['property'].split(';')
        trans_uris = [uri_to_fname(uri) for uri in uris]
        csv_fname = row['filename']+".csv"
        fdir = os.path.join(data_dir, csv_fname)
        preds = annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint,
                              data_dir="local_data", min_objs=MIN_NUM_OBJ, cols=[col_id], err_meth=err_meth)
        pconcept = row['pconcept']
        if pconcept in [None, np.nan, np.NaN]:
            print("is none")
            print(row)
        if pconcept not in eval_per_prop:
            eval_per_prop[pconcept] = []

        nrows = get_num_rows(fdir)

        diff_name = "%s-%s-%s" % (uri_to_fname(class_uri), uri_to_fname(uris[0]), fdir.split(os.sep)[-1])
        for c in preds:
            res = eval_column(preds[c], correct_uris=trans_uris, class_uri=class_uri, col_id=col_id, fdir=fdir,
                              diff_diagram=os.path.join("experiments", "diffs", folder_name, diff_name))
            # print("\n\n\nres: ")
            # print(res)
            files_k[fdir.split(os.sep)[-1]+"-"+str(c)] = (res, nrows)
            eval_data.append(res)
            eval_per_prop[pconcept].append(res)
        # if idx >= 12:
        #     if test:
        #         break
    prec, rec, f1 = compute_scores(eval_data, k=1)
    print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))
    compute_scores_per_property(eval_per_prop, "t2dv2")
    compute_counts(files_k, "t2dv2_datapoints")


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')
    parser.add_argument('-e', '--err-meth', default="mean_err", choices=["mean_err", "mean_sq_err"],
                        help="Functions to computer errors. ")
    parser.add_argument('-o', '--outlier-removal', default="true", choices=["true", "false"],
                        help="Whether to remove outliers or not")
    args = parser.parse_args()
    # parser.print_help()
    # raise Exception("")
    return args.err_meth, args.outlier_removal == "true"


if __name__ == '__main__':
    a = datetime.now()
    err_meth, outlier_removal = parse_arguments()
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=outlier_removal, err_meth=err_meth)
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

