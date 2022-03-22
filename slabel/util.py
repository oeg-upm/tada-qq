import os
from pandas.api.types import is_numeric_dtype
import pandas as pd


def create_dir(adir):
    if not os.path.exists(adir):
        os.makedirs(adir)


def save_objects(data_dir, class_uri, property_uri, objects):
    fdir = os.path.join(data_dir, uri_to_fname(class_uri), uri_to_fname(property_uri)) + ".txt"
    lines = [str(o) for o in objects]
    txt = "\n".join(lines)
    f = open(fdir, 'w')
    f.write(txt)
    f.close()


def data_exists(data_dir, class_uri, property_uri):
    fdir = os.path.join(data_dir, uri_to_fname(class_uri), uri_to_fname(property_uri))
    file_exists = os.path.exists(fdir)
    return file_exists


def fname_to_uri(fname, replace_sep=True):
    """

    """
    pref = {
        'dbo': 'dbpedia.org/ontology',
        'dbp': 'dbpedia.org/property',
        'dbr': 'dbpedia.org/resource',
        'foaf': 'xmlns.com/foaf/0.1',
        'owl': 'www.w3.org/2002/07/owl',
        'rdfs': 'www.w3.org/2000/01/rdf-schema',
        'rdf': 'www.w3.org/1999/02/22-rdf-syntax-ns',
    }
    protocol = "http://"
    base_uri = ""
    rel_name = ""
    for k in pref.keys():
        kd = k+"-"
        if fname.startswith(kd):
            base_uri = pref[k]
            rel_name = fname[len(kd):]
    rel_path = rel_name
    if replace_sep:
        rel_path = rel_name.replace('-', '/')
    uri = "/".join([protocol + base_uri, rel_path])
    return uri


def uri_to_fname(uri):
    """

    """
    fname = uri.strip().replace('http://', '')
    fname = fname.replace('dbpedia.org/ontology', 'dbo')
    fname = fname.replace('dbpedia.org/property', 'dbp')
    fname = fname.replace('dbpedia.org/resource', 'dbr')
    fname = fname.replace('xmlns.com/foaf/0.1', 'foaf')
    fname = fname.replace('www.w3.org/2002/07/owl', 'owl')
    fname = fname.replace('www.w3.org/2000/01/rdf-schema', 'rdfs')
    fname = fname.replace('www.w3.org/1999/02/22-rdf-syntax-ns', 'rdf')
    fname = fname.replace('/', '-')
    fname = fname.replace('#', '-')
    return fname


def property_dir_to_uri(fdir):
    class_name, prop_name = fdir.split(os.path.sep)[-2:]
    class_uri = fname_to_uri(class_name)
    property_uri = fname_to_uri(prop_name[:-4])
    return class_uri, property_uri


def get_columns_data(fdir, ids):
    """
    :param fdir:
    :return: list of the pair (colid, list)
    """
    # print("fdir: ")
    # print(fdir)
    df = pd.read_csv(fdir, thousands=',')
    numeric_cols = []
    for colid, col in enumerate(df):
        if colid in ids:
            # pair = (colid, list(df.iloc[:, colid]))
            # df_col = df[df.columns[colid]]
            h = df.columns[colid]

            # df_clean = df[~df[df.columns[colid]].isnull()]

            if not is_numeric_dtype(df[h]):
                df[h] = df[h].str.replace(',', '').astype(float, errors='ignore')

            df_clean = df

            # df['colname'] = df['colname'].str.replace(',', '').astype(float)

            # source: https://stackoverflow.com/questions/42192323/convert-pandas-dataframe-to-float-with-commas-and-negative-numbers
            # pd.to_numeric(df.str.replace(',',''), errors='coerce')
            # c = pd.to_numeric(df_clean[h].astype(str).replace(',', ''), errors='coerce')
            c = pd.to_numeric(df_clean[df_clean.columns[colid]], errors='coerce')
            c = c[~c.isnull()]
            pair = (colid, list(c))

            # pair = (colid, list(pd.to_numeric(df_clean[df_clean.columns[colid]], errors='coerce')[~df_clean[df_clean[df_clean.columns[0]]].isnull()]))
            # pair = (colid, list(pd.to_numeric(df.iloc[:, colid])))
            numeric_cols.append(pair)
    return numeric_cols
