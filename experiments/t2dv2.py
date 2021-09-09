import os

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.environ['t2dv2_dir']
meta_dir = os.path.join(data_dir, 'T2Dv2_typology.csv')


def get_numeric():
    """
    """

