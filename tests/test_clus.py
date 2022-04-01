import unittest
import os
import pandas as pd
from tadaqq.clus import Clusterer
from collections import Counter
from tadaqq.clus import Clusterer, PMap
from tadaqq.slabmer import SLabMer


def get_test_df():
    dbp = "http://dbpedia.org/property/"
    df = pd.DataFrame(
        [
            ['AAA', 'fnameaa1', 0, "1,2,3", "%spropa1;%spropa11" % (dbp, dbp)],
            ['AAA', 'fnameaa2', 0, "1,2,3,4", "%spropa11;%spropa12" % (dbp, dbp)],
            ['AAA', 'fnameaa3', 1, "1,6,5", "%spropa13;%spropa14;%spropa1" % (dbp, dbp, dbp)],

            ['AAA', 'fnameaa7', 2, "70,60,50", "%spropa3;%spropa31" % (dbp, dbp)],
            ['AAA', 'fnameaa8', 3, "70,60,50", "%spropa31" % dbp],
            ['AAA', 'fnameaa9', 1, "80,20,40", "%spropa31;%spropa34;%spropa3" % (dbp, dbp, dbp)],

            ['BBB', 'fnamebb1', 0, "1,2,3", "%spropb1;%spropb11" % (dbp, dbp)],
            ['BBB', 'fnamebb2', 0, "1,2,3,4", "%spropb11;%spropb12" % (dbp, dbp)],
            ['BBB', 'fnamebb3', 1, "1,6,5", "%spropb13;%spropb14;%spropb1" % (dbp, dbp, dbp)],

            ['CCC', 'fnamecc1', 0, "1000,2000,3000", "%spropc1;%spropc11" % (dbp, dbp)],
        ],
        columns=['concept', 'filename', 'columnid', 'col', 'property']
    )
    return df


def apply_cluster(df, fetch_method, err_meth, same_class, err_cutoff):
    clusterer = Clusterer(save_memory=False)
    pmap = PMap()
    for idx, row_and_i in enumerate(df.iterrows()):
        i, row = row_and_i
        pmap.add(row['property'].split(';'))
        col = [int(d) for d in row['col'].split(',')]
        ele = {
            'class_uri': 'http://dbpedia.org/ontology/' + row['concept'],
            'col_id': row['columnid'],
            'fname': row['filename'],
            'col': col,
            'num': len(col),
            'concept': row['concept'],
            'property': pmap.get(row['property'].split(';')[0]),
            'properties': row['property'].split(';')
        }
        clusterer.column_group_matching(ele, fetch_method, err_meth, err_cutoff, same_class)
    return clusterer


class ClusTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_evaluation(self):
        b = ["A", "A", "A", "B", "B", "B", "B", "B", "C", "C", "C"]
        c = Counter(b)
        a = [["A", "A", "A", "B", "B", "B"], ["B", "B"], ["C", "C", "C"]]
        groups = []
        for g in a:
            clus = [{'gs_clus': cl} for cl in g]
            groups.append(clus)
        clusterer = Clusterer()
        clusterer.groups = groups
        p, r, f1 = clusterer.evaluate(c)
        self.assertEqual(p, 2/3)
        self.assertEqual(r, 2.6/3)

    def test_group_matching(self):
        groups = []
        eles = []
        ele = {'col': [1, 2, 3]}
        eles.append(ele)
        ele = {'col': [1, 2, 4]}
        eles.append(ele)
        ele = {'col': [20, 20, 30]}
        eles.append(ele)
        ele = {'col': [21, 21, 31]}
        eles.append(ele)
        ele = {'col': [24, 24, 34]}
        eles.append(ele)
        ele = {'col': [140, 240, 340]}
        eles.append(ele)
        err_cutoff = 0.3
        err_meth = "mean_err"
        fetch_method = "max"
        clusterer = Clusterer()
        clusterer.groups = groups
        for ele in eles:
            ele['num'] = len(ele['col'])
            clusterer.column_group_matching(ele, fetch_method, err_meth, err_cutoff, False)
        self.assertEqual(len(groups), 3)
        self.assertEqual(len(groups[0]), 2)
        self.assertEqual(len(groups[1]), 3)
        self.assertEqual(len(groups[2]), 1)

    def test_clusterer(self):
        df = get_test_df()
        clusterer = apply_cluster(df, fetch_method="max", err_meth="mean_err", err_cutoff=0.3, same_class=False)
        self.assertEqual(len(clusterer.groups), 3)
        clusterer = apply_cluster(df, fetch_method="max", err_meth="mean_err", err_cutoff=0.3, same_class=True)
        self.assertEqual(len(clusterer.groups), 4)


if __name__ == '__main__':
    unittest.main()
