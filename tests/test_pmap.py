import unittest
import os
import pandas as pd
from tadaqq.clus import PMap
from collections import Counter


class PMapTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_pmap(self):
        pmap = PMap()
        pmap.add(['A', 'B', 'C'])
        self.assertIn('A', pmap.mappings)
        self.assertIn('B', pmap.mappings)
        self.assertIn('C', pmap.mappings)
        self.assertEqual(pmap.get('B'), 'A')
        pmap.add(['X', 'Y', 'Z'])
        self.assertIn('X', pmap.mappings)
        self.assertIn('Y', pmap.mappings)
        self.assertIn('Z', pmap.mappings)
        self.assertEqual(pmap.get('C'), 'A')
        self.assertEqual(pmap.get('X'), 'X')
        self.assertEqual(pmap.get('Z'), 'X')


if __name__ == '__main__':
    unittest.main()

