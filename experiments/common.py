import os
import logging

import pandas as pd
from pandas.api.types import is_numeric_dtype
from easysparql import easysparqlclass

from qq.qqe import QQE
from qq.dist import get_data


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# logger = get_logger(__name__, level=logging.INFO)
logger = get_logger(__name__, level=logging.DEBUG)


esparql = easysparqlclass.EasySparql(cache_dir=".cache", logger=logger)


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


def get_candidate_properties(class_uri, sample_data, data_dir):
    """
    :param class_uri:
    :param sample_data:
    :param data_dir:
    :return: list of pairs. each pair os composed of (mean_err, prop-fname)
    """
    class_fname = uri_to_fname(class_uri)
    class_dir = os.path.join(data_dir, class_fname)
    qqe = QQE(sample_data)
    fnames = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    errs = []
    for f in fnames:
        prop_dir = os.path.join(class_dir, f)
        prop_data = get_data(prop_dir)
        err = qqe.predict_and_get_mean_error(prop_data, remove_outliers=True)
        item = (err, f)
        errs.append(item)

    errs.sort()
    return errs


def collect_numeric_data(class_uri, endpoint, data_dir, min_objs):
    """
    :param class_uri:
    :param endpoint:
    :param data_dir:
    :return:
    """

    prop_query = """select distinct ?p where{
        ?s a <%s>.
        ?s ?p ?o.
    }
    """ % (class_uri)

    query_template = """select ?o where{
        ?s a <%s>.
        ?s <%s> ?o.
    }
    """

    create_dir(data_dir)
    class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
    if os.path.exists(class_dir):
        return
    create_dir(class_dir)
    esparql.endpoint = endpoint
    results = esparql.run_query(prop_query)
    properties = [r['p']['value'] for r in results]
    for prop in properties:
        if data_exists(data_dir=data_dir, class_uri=class_uri, property_uri=prop):
            continue
        query = query_template % (class_uri, prop)
        results = esparql.run_query(query=query)
        if results is None:
            logger.debug('No results for the query: ' + query)
            continue
        objects = [r['o']['value'] for r in results]
        if len(objects) >= min_objs:
            nums = esparql.get_numerics_from_list(objects, 0.5)
            if nums is None:
                logger.debug('property is not numeric: ' + prop)
                continue
            elif len(nums) >= min_objs:
                logger.debug('saving property: ' + prop)
                save_objects(data_dir, class_uri, prop, nums)
            else:
                logger.debug("less than 30 numeric values: " + prop)
        else:
            logger.debug('less than 30 objects: ' + prop)


def create_dir(adir):
    if not os.path.exists(adir):
        os.makedirs(adir)


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


def annotate_file(fdir, class_uri, endpoint, remove_outliers, data_dir, min_objs, cols=[]):
    """
    :param fdir: of the csv file to be annotated
    :param class_uri:
    :param endpoint:
    :param remove_outliers: True/False
    :param data_dir:
    :param cols: list of int - the ids of the numeric columns. If nothing is passed, the function will detect
    numeric columns
    :return: dict
     {
        'colid1': errs1,
        'colid2': errs1,
     }

    errs => list of pairs
        a pair is composed of <distance or error val, fname>
    """
    collect_numeric_data(class_uri=class_uri, endpoint=endpoint, data_dir=data_dir, min_objs=min_objs)
    if not cols:
        num_cols = get_numeric_columns(fdir)
    else:
        num_cols = get_columns_data(fdir, cols)
    class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
    properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]
    # logger.info("File: "+fdir.split('/')[-1])
    preds = dict()
    for colobj in num_cols:
        colid, coldata = colobj
        logger.info('%s - (col=%d) ' % (fdir.split('/')[-1], colid))
        # logger.info('Column: ' + str(colid))
        errs = annotate_column(col=coldata, properties_dirs=properties_dirs, remove_outliers=remove_outliers)
        preds[colid] = errs
    return preds


def get_numeric_columns(fdir):
    """
    :param fdir:
    :return: list of the pair (colid, list)
    """
    df = pd.read_csv(fdir)
    numeric_cols = []
    for col in df:
        if is_numeric_dtype(df[col]):
            pair = (col, list(df[col]))
            numeric_cols.append(pair)
    return numeric_cols


def get_columns_data(fdir, ids):
    """
    :param fdir:
    :return: list of the pair (colid, list)
    """
    df = pd.read_csv(fdir, thousands=',')
    numeric_cols = []
    for colid, col in enumerate(df):
        if colid in ids:
            # pair = (colid, list(df.iloc[:, colid]))
            # df_col = df[df.columns[colid]]
            df_clean = df[~df[df.columns[colid]].isnull()]
            c = pd.to_numeric(df_clean[df_clean.columns[colid]], errors='coerce')
            c = c[~c.isnull()]
            pair = (colid, list(c))

            # pair = (colid, list(pd.to_numeric(df_clean[df_clean.columns[colid]], errors='coerce')[~df_clean[df_clean[df_clean.columns[0]]].isnull()]))
            # pair = (colid, list(pd.to_numeric(df.iloc[:, colid])))
            numeric_cols.append(pair)
    return numeric_cols


def annotate_column(col, properties_dirs, remove_outliers):
    print("annotate_column> col:")
    print(col)
    qqe = QQE(col)
    errs = []
    for prop_f in properties_dirs:
        objects = get_data(prop_f)
        err = qqe.predict_and_get_mean_error(objects, remove_outliers=remove_outliers)
        item = (err, prop_f)
        errs.append(item)
    errs.sort()
    return errs


def property_dir_to_uri(fdir):
    class_name, prop_name = fdir.split(os.path.sep)[-2:]
    class_uri = fname_to_uri(class_name)
    property_uri = fname_to_uri(prop_name[:-4])
    return class_uri, property_uri


def eval_column(p_errs, correct_uris=[]):
    """
    p_errs: a list of pairs. each pair starts with the error/distance and the filename
        (e.g., <0.1, dbo-Person-abc/dbp-xyz.txt>)
    k: consider the prediction correct if it is in the top k.
        Check if prediction is correct or not
    """
    k = -1
    for idx, item in enumerate(p_errs):
        trans_uri = item[1].split('/')[-1][:-4]
        trans_uri = uri_to_fname(trans_uri)
        if idx<3:
            logger.info("%d err: %.2f - %s - %s" % (idx+1, item[0], item[1], property_dir_to_uri(item[1])[1]))
            # logger.info(str(idx+1)+" err: "+str(item[0]) + "  - " + item[1] + " - "+property_dir_to_uri(item[1])[1])
        if trans_uri in correct_uris:
            k = idx + 1
            break
    return k


def compute_scores(eval_data, k=1):
    """
    """
    corr = 0
    incorr = 0
    notf = 0
    for d in eval_data:
        if d == -1:
            notf +=1
        elif d <=k:
            corr += 1
        else:
            incorr += 1
    if corr == 0:
        prec = 0
        rec = 0
        f1 = 0
    else:
        prec = corr/ (corr+incorr)
        rec = corr / (corr+notf)
        f1 = 2*prec*rec / (prec+rec)
    print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))
