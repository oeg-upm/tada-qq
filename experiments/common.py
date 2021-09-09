import os
import logging

import pandas as pd
from pandas.api.types import is_numeric_dtype
from easysparql import easysparql

from qq.qqe import QQE
from qq.dist import get_data


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__, level=logging.DEBUG)


def save_objects(data_dir, class_uri, property_uri, objects):
    fdir = os.path.join(data_dir, uri_to_fname(class_uri), uri_to_fname(property_uri)) + ".txt"
    # fname = uri_to_fname(class_uri) + " - " + uri_to_fname(property_uri)
    lines = [str(o) for o in objects]
    txt = "\n".join(lines)
    f = open(fdir, 'w')
    f.write(txt)
    f.close()


def data_exists(data_dir, class_uri, property_uri):
    # print("data_dir: ")
    # print(data_dir)
    # print("class uri: ")
    # print(class_uri)
    # print("property uri: ")
    # print(property_uri)
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
    # logger.debug("sample data: ")
    # logger.debug(sample_data)
    qqe = QQE(sample_data)
    fnames = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    # fnames = [f for f in fnames if f[:-4] == ".txt"]
    # logger.debug("fnames: ")
    # logger.debug(fnames)
    errs = []
    for f in fnames:
        prop_dir = os.path.join(class_dir, f)
        prop_data = get_data(prop_dir)
        err = qqe.predict_and_get_mean_error(prop_data, remove_outliers=True)
        item = (err, f)
        errs.append(item)
        # print(item)

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

    results = easysparql.run_query(prop_query, endpoint=endpoint)
    properties = [r['p']['value'] for r in results]
    for prop in properties:
        if data_exists(data_dir=data_dir, class_uri=class_uri, property_uri=prop):
            continue
        query = query_template % (class_uri, prop)
        results = easysparql.run_query(query=query, endpoint=endpoint)
        if results is None:
            logger.debug('No results for the query: ' + query)
            continue
        objects = [r['o']['value'] for r in results]
        if len(objects) >= min_objs:
            nums = easysparql.get_numerics_from_list(objects, 0.5)
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


def annotate_file(fdir, class_uri, endpoint, remove_outliers, data_dir, min_objs):
    """
    :param fdir: of the csv file to be annotated
    :param class_uri:
    :param endpoint:
    :param remove_outliers: True/False
    :param data_dir:
    :return:
    """
    # print("class_uri: ")
    # print(class_uri)
    collect_numeric_data(class_uri=class_uri, endpoint=endpoint,data_dir=data_dir, min_objs=min_objs)
    num_cols = get_numeric_columns(fdir)
    class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
    # print("class_dir: ")
    # print(class_dir)
    properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]
    logger.info("\n\n\nFile: "+fdir.split('/')[-1])
    # print(properties_dirs)
    for colobj in num_cols:
        colid, coldata = colobj
        logger.info('\nColumn: ' + str(colid))
        annotate_column(col=coldata, properties_dirs=properties_dirs, remove_outliers=remove_outliers)


def get_numeric_columns(fdir):
    """
    :param fdir:
    :return: list of the pair (colid, list)
    """
    df = pd.read_csv(fdir)
    # print(df)
    numeric_cols = []
    for col in df:
        # print("\n\n\n=========================")
        # print(col)
        # print(df[col].dtype)
        if is_numeric_dtype(df[col]):
            pair = (col, list(df[col]))
            numeric_cols.append(pair)
    # logger.debug("Get numeric columns:")
    # logger.debug(numeric_cols)
    return numeric_cols


def annotate_column(col, properties_dirs, remove_outliers):
    # print("\n\ncol: ")
    # print(col)
    qqe = QQE(col)
    errs = []
    for prop_f in properties_dirs:
        objects = get_data(prop_f)
        # print("objects: ")
        # print(objects)
        err = qqe.predict_and_get_mean_error(objects, remove_outliers=remove_outliers)
        item = (err, prop_f)
        errs.append(item)
    errs.sort()
    for idx, item in enumerate(errs[:10]):
        logger.info(str(idx+1)+" err: "+str(item[0]) + "  - " + item[1])
