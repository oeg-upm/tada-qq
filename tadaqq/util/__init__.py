import os
import pandas as pd
from pandas.api.types import is_numeric_dtype


def compute_scores(eval_data, k=1):
    """
    """
    corr = 0
    incorr = 0
    notf = 0
    for d in eval_data:
        if d == -1:
            notf += 1
        elif d <= k:
            corr += 1
        elif d < 1:
            err_msg = "Error: compute_scores> Invalid k <%s>" % str(d)
            print(err_msg)
            raise Exception(err_msg)
        else:
            incorr += 1
    if corr == 0:
        prec = 0
        rec = 0
        f1 = 0
    else:
        prec = corr / (corr+incorr)
        rec = corr / (corr+notf)
        f1 = 2*prec*rec / (prec+rec)
    return prec, rec, f1


def get_data(fname):
    """
    :param fname:
    :return:
    """
    a = []
    f = open(fname)
    for line in f.readlines():
        if line.strip() != "":
            a.append(float(line))
    f.close()
    return a


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
    df = pd.read_csv(fdir, thousands=',')
    numeric_cols = []
    for colid, col in enumerate(df):
        if colid in ids:
            h = df.columns[colid]

            if not is_numeric_dtype(df[h]):
                df[h] = df[h].str.replace(',', '').astype(float, errors='ignore')

            df_clean = df
            c = pd.to_numeric(df_clean[df_clean.columns[colid]], errors='coerce')
            c = c[~c.isnull()]
            pair = (colid, list(c))
            numeric_cols.append(pair)
    return numeric_cols
