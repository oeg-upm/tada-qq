from datetime import datetime
import os
from experiments.common import annotate_file, eval_column, compute_scores, uri_to_fname
import pandas as pd

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_t2dv2(endpoint, remove_outliers):
    """
    endpoint:
    remove_outliers: bool
    filename,concept,k,column,property,columnid,kind,sub_kind
    """
    # f = open(meta_dir)
    eval_data = []
    df = pd.read_csv(meta_dir)
    df = df[df.property.notnull()]
    df = df[df["concept"].notnull()]
    for idx, row in df.iterrows():
        # fname = atts[0].strip()
        class_uri = 'http://dbpedia.org/ontology/'+row['concept']
        col_id = int(row['columnid'])
        uris = row['property'].split(';')
        trans_uris = [uri_to_fname(uri) for uri in uris]
        csv_fname = row['filename']+".csv"
        fdir = os.path.join(data_dir, csv_fname)
        preds = annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint,
                              data_dir="local_data", min_objs=MIN_NUM_OBJ, cols=[col_id])
        for c in preds:
            res = eval_column(preds[c], correct_uris=trans_uris)
            eval_data.append(res)
            if not res:
                print(preds)
    # for line in f.readlines():
    #     print(line)
    #     atts = line.split(',')
    #     if len(atts) > 1:
    #         fname = atts[0].strip()
    #         class_uri = atts[1].strip()
    #         col_id = int(atts[2])
    #         uris = atts[3].split(';')
    #         trans_uris = [uri_to_fname(uri) for uri in uris]
    #         fdir = os.path.join(data_dir, fname)
    #         preds = annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint,
    #                       data_dir=data_dir, min_objs=MIN_NUM_OBJ, cols=[col_id])
    #         for c in preds:
    #             res = eval_column(preds[c], correct_uris=trans_uris)
    #             eval_data.append(res)
    #             if not res:
    #                 print(preds)
    print("results: ")
    print(eval_data)
    compute_scores(eval_data, k=1)


if __name__ == '__main__':
    a = datetime.now()
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=True)
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

