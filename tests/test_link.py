import unittest
import os
import pandas as pd
from link import common
from collections import Counter


class LinkTest(unittest.TestCase):

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
        p, r, f1 = common.evaluate(groups, c)
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
        for ele in eles:
            ele['num'] = len(ele['col'])
            common.column_group_matching(groups, ele, fetch_method, err_meth, err_cutoff)

        # for g in groups:
        #     print(g)
        #     print("=======")
        self.assertEqual(len(groups), 3)
        self.assertEqual(len(groups[0]), 2)
        self.assertEqual(len(groups[1]), 3)
        self.assertEqual(len(groups[2]), 1)


if __name__ == '__main__':
    unittest.main()
