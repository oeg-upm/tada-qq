from datetime import datetime
import os
import argparse

import numpy as np

from experiments.common import annotate_file, eval_column, compute_scores, uri_to_fname, compute_scores_per_property
from experiments.common import get_num_rows, compute_counts, compute_counts_per_err_meth
import pandas as pd

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')
# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_t2dv2(endpoint, remove_outliers, err_meths, loose=False, estimate=[True], diffs=False):
    """
    endpoint:
    remove_outliers: bool
    filename,concept,k,column,property,columnid,kind,sub_kind
    """
    err_meth_scores = dict()
    print("\n\n|Quantile Prediction\t|Error Function\t|Precision\t|Recall\t|F1\t|")
    print("|:------:|:------:|:---------:|:------:|:---:|")
    for use_estimate in estimate:
        for err_meth in err_meths:
            eval_data = []
            df = pd.read_csv(meta_dir)
            df = df[df.property.notnull()]
            df = df[df["concept"].notnull()]
            df = df[df["pconcept"].notnull()]
            if not loose:
                df = df[df["loose"] != "yes"]
            test = True
            if err_meth == "mean_err":
                folder_name = "t2dv2-mean-err"
            elif err_meth == "mean_sq_err":
                folder_name = "t2dv2-mean-sq-err"
            elif err_meth == "mean_sq1_err":
                folder_name = "t2dv2-mean-sq1-err"
            elif err_meth == "mean_sqroot_err":
                folder_name = "t2dv2-mean-sqroot-err"
            else:
                raise Exception("unknown err method")
            if use_estimate:
                folder_name += "-estimate"
                est_txt = "estimate"
            else:
                folder_name += "-exact"
                est_txt = "exact"
            if loose:
                folder_name += "-loose"
            if not remove_outliers:
                folder_name += "-raw"
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
                                      data_dir="local_data", min_objs=MIN_NUM_OBJ, cols=[col_id], err_meth=err_meth,
                                      estimate=use_estimate)
                pconcept = row['pconcept']
                if pconcept in [None, np.nan, np.NaN]:
                    print("is none")
                    print(row)
                if pconcept not in eval_per_prop:
                    eval_per_prop[pconcept] = []
                nrows = get_num_rows(fdir)
                diff_name = "%s-%s-%s" % (uri_to_fname(class_uri), uri_to_fname(uris[0]), fdir.split(os.sep)[-1])
                diff_folder_path = os.path.join("experiments", "diffs", folder_name)
                if not os.path.exists(diff_folder_path):
                    os.mkdir(diff_folder_path)
                for c in preds:
                    diff_path = os.path.join(diff_folder_path, diff_name)
                    if not diffs:
                        diff_path = None
                    res = eval_column(preds[c], correct_uris=trans_uris, class_uri=class_uri, col_id=col_id, fdir=fdir,
                                      diff_diagram=diff_path)
                    # print("\n\n\nres: ")
                    # print(res)
                    files_k[fdir.split(os.sep)[-1]+"-"+str(c)] = (res, nrows)
                    eval_data.append(res)
                    eval_per_prop[pconcept].append(res)
                # Testing
                # if idx >= 1:
                #     if test:
                #         print("res: ")
                #         print(res)
                #         break
            prec, rec, f1 = compute_scores(eval_data, k=1)
            # print("\n\n|Quantile Prediction\t|Error Function\t|Precision\t|Recall\t|F1\t|")
            # print("|:------:|:------:|:---------:|:------:|:---:|")
            print("|%s\t|%s\t|%.2f\t|%.2f\t|%.2f\t|" % (est_txt, err_meth, prec, rec, f1))
            # print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))
            compute_scores_per_property(eval_per_prop, folder_name)
            # Commented for testing only
            scores_df = compute_counts(files_k, "datapoints-%s" % (folder_name))

            if est_txt not in err_meth_scores:
                err_meth_scores[est_txt] = dict()

            err_meth_scores[est_txt][err_meth] = scores_df
    fname = "t2dv2-err-methods"
    if not remove_outliers:
        fname += "-raw"
    compute_counts_per_err_meth(err_meth_scores, fname)


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')
    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+",
                        help="Functions to computer errors.")
    parser.add_argument('-o', '--outlier-removal', default="true", choices=["true", "false"],
                        help="Whether to remove outliers or not.")
    parser.add_argument('-l', '--loose', action='store_true')
    parser.add_argument('-d', '--diff', action='store_true', help="Store the diffs")
    parser.add_argument('-s', '--estimate', default=["True"], nargs="+")
    args = parser.parse_args()
    # parser.print_help()
    # raise Exception("")
    estimates = [e.lower() == "true" for e in args.estimate]
    return args.err_meths, args.outlier_removal == "true", args.loose, estimates, args.diff


if __name__ == '__main__':
    a = datetime.now()
    err_meths, outlier_removal, loose, estimate, diffs = parse_arguments()

    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=outlier_removal, err_meths=err_meths,
                   estimate=estimate, loose=loose, diffs=diffs)
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

