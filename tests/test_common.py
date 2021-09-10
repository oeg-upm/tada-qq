import unittest
import numpy as np
from qq.qqe import QQE
from experiments import common


class CommonTest(unittest.TestCase):

    def test_fname_to_uri(self):
        uri = common.fname_to_uri("dbo-Person-abc")
        corr = "http://dbpedia.org/ontology/Person/abc"
        self.assertEqual(uri, corr)

        uri = common.fname_to_uri("dbo-abc")
        corr = "http://dbpedia.org/ontology/abc"
        self.assertEqual(uri, corr)

        uri = common.fname_to_uri("dbp-abc")
        corr = "http://dbpedia.org/property/abc"
        self.assertEqual(uri, corr)

    def test_prop_fdir_to_uri(self):
        c, p = common.property_dir_to_uri("local_data/dbo-Person-abc/dbp-xyz.txt")
        class_uri = "http://dbpedia.org/ontology/Person/abc"
        property_uri = "http://dbpedia.org/property/xyz"
        self.assertEqual(c, class_uri)
        self.assertEqual(p, property_uri)


if __name__ == '__main__':
    unittest.main()