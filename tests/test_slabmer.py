import unittest
import os
import pandas as pd
from tadaqq.clus import Clusterer, PMap
from tadaqq.slabmer import SLabMer
from collections import Counter
from tadaqq.util import get_columns_data

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"


def get_col(fname, colid):
    data_dir = os.path.join('tests', 'test_files')
    fpath = os.path.join(data_dir, fname)
    cols = get_columns_data(fpath, [colid])
    return cols[0][1]


def apply_cluster(df, fetch_method, err_meth, same_class, err_cutoff):
    clusterer = Clusterer(save_memory=False)
    pmap = PMap()
    for idx, row_and_i in enumerate(df.iterrows()):
        i, row = row_and_i
        pmap.add(row['property'].split(';'))
        col = get_col(row['filename'], int(row['columnid']))

        ele = {
            'class_uri': row['class_uri'],
            'col_id': row['columnid'],
            'fname': row['filename'],
            'col': col,
            'num': len(col),
            'concept': row['class_uri'].split('/')[-1],
            'property': pmap.get(row['property'].split(';')[0]),
            'properties': row['property'].split(';')
        }
        clusterer.column_group_matching(ele, fetch_method, err_meth, err_cutoff, same_class)
    return clusterer


class SLabMerTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_slabmer_perfect(self):
        base_dir = os.path.join('tests', 'test_files')
        meta_df = pd.read_csv(os.path.join(base_dir, 'meta-basketball.csv'))
        clusterer = apply_cluster(meta_df, fetch_method="max", err_meth="mean_err", err_cutoff=0.15, same_class=False)
        self.assertEqual(len(clusterer.groups), 2)
        slabmer = SLabMer(SPARQL_ENDPOINT)
        slabmer.annotate_clusters(clusterer.groups, remove_outliers=False, estimate=True, err_meth="mean_err",
                                  candidate_failback=False, k=1)
        score = slabmer.evaluate_labelling(clusterer.groups)
        self.assertEqual(score['prec'], 1.0)
        self.assertEqual(score['rec'], 1.0)
        self.assertEqual(score['f1'], 1.0)

    def test_slabmer_precision(self):
        base_dir = os.path.join('tests', 'test_files')
        meta_df = pd.read_csv(os.path.join(base_dir, 'meta-mountain.csv'))
        clusterer = apply_cluster(meta_df, fetch_method="max", err_meth="mean_err", err_cutoff=0.15, same_class=False)
        self.assertEqual(len(clusterer.groups), 2)
        slabmer = SLabMer(SPARQL_ENDPOINT)
        slabmer.annotate_clusters(clusterer.groups, remove_outliers=False, estimate=True, err_meth="mean_err",
                                  candidate_failback=False, k=100)
        score = slabmer.evaluate_labelling(clusterer.groups)
        self.assertLess(score['prec'], 0.7)
        self.assertEqual(score['rec'], 1.0)


if __name__ == '__main__':
    unittest.main()
