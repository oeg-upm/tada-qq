import unittest
from tadaqq import util
import os
import shutil


class UtilTest(unittest.TestCase):

    def test_fname_to_uri(self):
        uri = util.fname_to_uri("dbo-Person-abc")
        corr = "http://dbpedia.org/ontology/Person/abc"
        self.assertEqual(uri, corr)

        uri = util.fname_to_uri("dbo-abc")
        corr = "http://dbpedia.org/ontology/abc"
        self.assertEqual(uri, corr)

        uri = util.fname_to_uri("dbp-abc")
        corr = "http://dbpedia.org/property/abc"
        self.assertEqual(uri, corr)

    def test_prop_fdir_to_uri(self):
        c, p = util.property_dir_to_uri("local_data/dbo-Person-abc/dbp-xyz.txt")
        class_uri = "http://dbpedia.org/ontology/Person/abc"
        property_uri = "http://dbpedia.org/property/xyz"
        self.assertEqual(c, class_uri)
        self.assertEqual(p, property_uri)

    def test_save_objects(self):
        class_uri = "http://dbpedia.org/ontology/example"
        property_uri = "http://dbpedia.org/property/height"
        class_folder = "dbo-example"
        property_folder = "dbp-height.txt"
        data_folder = "test_files"
        class_dir = os.path.join(data_folder, class_folder)
        if os.path.exists(class_dir):
            shutil.rmtree(class_dir)
            # os.rmdir(class_dir)
        util.create_dir(class_dir)
        util.save_objects("test_files", class_uri, property_uri, ["a", "b", "c"])
        fdir = os.path.join(class_dir, property_folder)
        text = ""
        with open(fdir) as f:
            text += f.read()
        self.assertGreater(len(text), 2)


if __name__ == '__main__':
    unittest.main()