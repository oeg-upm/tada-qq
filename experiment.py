import os
import logging
from qqe import QQE
from easysparql import easysparql
from dist import get_data
import pandas as pd
from pandas.api.types import is_numeric_dtype
from datetime import datetime

data_dir = "local_data"

# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__, level=logging.DEBUG)
# logger = get_logger(__name__, level=logging.INFO)


def create_dir(adir):
    if not os.path.exists(adir):
        os.makedirs(adir)


def uri_to_fname(uri):
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


def fname_to_uri(fname):
    uri = fname.strip()[:-4]
    uri = uri.replace('dbo-', 'http://dbpedia.org/ontology/')
    uri = uri.replace('dbp-', 'http://dbpedia.org/property/')
    uri = uri.replace('dbr-', 'http://dbpedia.org/resource/')
    uri = uri.replace('foaf-', 'http://xmlns.com/foaf/0.1/')
    uri = uri.replace('owl-', 'http://www.w3.org/2002/07/owl#')
    uri = uri.replace('rdfs-', 'http://www.w3.org/2000/01/rdf-schema#')
    uri = uri.replace('rdf-', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    # Filter out the class
    start_idx = uri.find('http://')
    uri = uri[start_idx+1:]
    # Get to the property
    start_idx = uri.find('http://')
    uri = uri[start_idx:]
    return uri


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


# def collect_numeric_data(class_uri, endpoint):
#     query_template = """select ?o where{
#         ?s a <%s>.
#         ?s <%s> ?o.
#     }
#     """
#     create_dir(data_dir)
#     class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
#     if os.path.exists(class_dir):
#         return
#     create_dir(class_dir)
#     subjects = easysparql.get_subjects(class_uri=class_uri, endpoint=endpoint)
#     logger.debug('num of subjects is: '+str(len(subjects)))
#     total_num = len(subjects)
#     for idx, subject in enumerate(subjects):
#         logger.debug(" %d from %d" % (idx, total_num))
#         properties = easysparql.get_properties_of_subject(subject_uri=subject, endpoint=endpoint)
#         for prop in properties:
#             if data_exists(data_dir=data_dir,class_uri=class_uri, property_uri=prop):
#                 continue
#             query = query_template % (class_uri, prop)
#             results = easysparql.run_query(query=query, endpoint=endpoint)
#             if results is None:
#                 logger.debug('No results for the query: '+query)
#                 continue
#             objects = [r['o']['value'] for r in results]
#             if len(objects) >= MIN_NUM_OBJ:
#                 nums = easysparql.get_numerics_from_list(objects, 0.5)
#                 if nums is None:
#                     logger.debug('property is not numeric: '+prop)
#                     continue
#                 elif len(nums) >= MIN_NUM_OBJ:
#                     logger.debug('saving property: '+prop)
#                     save_objects(data_dir, class_uri, prop, nums)
#                 else:
#                     logger.debug("less than 30 numeric values: "+prop)
#             else:
#                 logger.debug('less than 30 objects: '+prop)
#
#     # for each, get properties
#     # for each, get count
#     # check if numeric
#     # for numerics, if count > 30, consider


def collect_numeric_data(class_uri, endpoint):
    """
    :param class_uri:
    :param endpoint:
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
        if len(objects) >= MIN_NUM_OBJ:
            nums = easysparql.get_numerics_from_list(objects, 0.5)
            if nums is None:
                logger.debug('property is not numeric: ' + prop)
                continue
            elif len(nums) >= MIN_NUM_OBJ:
                logger.debug('saving property: ' + prop)
                save_objects(data_dir, class_uri, prop, nums)
            else:
                logger.debug("less than 30 numeric values: " + prop)
        else:
            logger.debug('less than 30 objects: ' + prop)


# def aaa():
#     data_dir = 'local_data/dbo-BasketballPlayer'
#     a = get_data("local_olympic_basketball_height_cm.txt")
#     qqe = QQE(a)
#     fnames = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
#     errs = []
#     for fname in fnames:
#         sample = get_data(os.path.join(data_dir, fname))
#         err = qqe.compute_error_mean(sample, remove_outliers=True)
#         logger.debug("mean: "+(str(err))+"  - "+fname)
#         item = (err, fname)
#         errs.append(item)
#
#     errs.sort()
#     for item in errs:
#         logger.debug("err: "+str(item[0]) + "  - " + item[1])


def get_candidate_properties(class_uri, sample_data):
    """
    :param class_uri:
    :param sample_data:
    :return: list of pairs. each pair os composed of (mean_err, prop-fname)
    """
    global data_dir
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
        err = qqe.compute_error_mean(prop_data, remove_outliers=True)
        item = (err, f)
        errs.append(item)
        # print(item)

    errs.sort()
    return errs


def annotate_a_col_in_file(fdir, class_uri, endpoint, remove_outliers, colid):
    """
    Similar to the function `annotate_file` but the difference is that this expects a colid
    :return: list of the pair (err, property_uri)
    """
    collect_numeric_data(class_uri=class_uri, endpoint=endpoint)
    class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
    properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]
    col = get_column(fdir, colid)
    num_col = easysparql.get_numerics_from_list(col, 0)
    print("col: ")
    print(num_col)
    return annotate_column(col=num_col, properties_dirs=properties_dirs, remove_outliers=remove_outliers)


def annotate_file(fdir, class_uri, endpoint, remove_outliers):
    """
    :param fdir: of the csv file to be annotated
    :param class_uri:
    :param endpoint:
    :param remove_outliers: True/False
    :return:
    """
    global data_dir
    # print("class_uri: ")
    # print(class_uri)
    collect_numeric_data(class_uri=class_uri, endpoint=endpoint)
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


def annotate_column(col, properties_dirs, remove_outliers):
    """
    :param col:
    :param properties_dirs:
    :param remove_outliers:
    :return: list of the pair (err,property)
    """
    # print("\n\ncol: ")
    # print(col)
    qqe = QQE(col)
    errs = []
    for prop_f in properties_dirs:
        objects = get_data(prop_f)
        # print("objects: ")
        # print(objects)
        err = qqe.compute_error_mean(objects, remove_outliers=remove_outliers)
        item = (err, prop_f)
        errs.append(item)
    errs.sort()
    for idx, item in enumerate(errs[:10]):
        logger.info(str(idx+1)+" err: "+str(item[0]) + "  - " + item[1])
    return errs


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


def get_column(fdir, colid):
    """
    :param fdir:
    :param colid:
    :return: a list of the cells of the colid
    """
    print("open: "+fdir)
    df = pd.read_csv(fdir)
    df = df[df.iloc[:, colid].notnull()]
    col = list(df.iloc[:, colid])
    # col = list(df[df.columns[colid]])
    return col


def annotate_olympic_games(endpoint, remove_outliers):
    olympic_games_dir = 'olympic_games'
    olympic_games_data_dir = os.path.join(data_dir, olympic_games_dir, 'data')
    meta_dir = os.path.join(data_dir, olympic_games_dir, 'meta.csv')
    f = open(meta_dir)
    for line in f.readlines():
        atts = line.split(',')
        if len(atts) > 1:
            fname = atts[0].strip()
            class_uri = atts[1].strip()
            fdir = os.path.join(olympic_games_data_dir, fname)
            annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint)


def get_k_from_errs(errs, property_uri):
    """
    :param errs: list of pairs (err, property_uri)
    :param property_uri: the correct property_uri
    :return:
    """
    # logger.debug("Top: "+errs[0][1] + " ("+property_uri+")")
    g_prop_name = property_uri.split('/')[-1]
    for idx, pair in enumerate(errs):
        k = idx+1
        err, prop_path = pair
        curr_prop_uri = fname_to_uri(prop_path).strip()
        if curr_prop_uri == property_uri:
            return k
        else:
            logger.debug("Checking %s  ---  %s" % (curr_prop_uri, property_uri))
    return -1

    # logger.debug("Top: "+errs[0][1] + " ("+property_uri+")")
    # g_prop_name = property_uri.split('/')[-1]
    # for idx, pair in enumerate(errs):
    #     k = idx+1
    #     err, prop_path = pair
    #     prop_last = prop_path.split('/')[-1]
    #     prop_name = prop_last[4:-4]
    #     if prop_name == g_prop_name:
    #         return k
    #     else:
    #         logger.debug("Checking %s  ---  %s" % (prop_name, g_prop_name))
    # return -1


def compute_scores(ks):
    """
    :param ks:
    :return:
    """
    num_corr =0
    num_incorr =0
    num_notfound =0
    rr = 0
    num_rr = 0
    for k in ks:
        if k < 0:
            num_notfound +=1
        elif k==1:
            num_corr+=1
        elif k > 1:
            num_incorr+=1
        else:
            logger.error("ERROR .. invalid k")
        if k > 0:
            rr += 1.0 / k
            num_rr += 1
    if num_rr == 0:
        mrr = 0
    else:
        mrr = rr/num_rr
    if num_corr + num_incorr == 0:
        pre = 0
    else:
        pre = num_corr / (num_corr + num_incorr)
    if num_corr + num_notfound == 0:
        rec = 0
    else:
        rec = num_corr / (num_corr + num_notfound)
    if pre+rec == 0:
        f1 = 0
    else:
        f1 = 2.0 * pre * rec / (pre + rec)
    print("MRR: %f\nPrecision: %f\nRecall: %f\nF1: %f" % (mrr, pre, rec, f1))


def append_results(fdir, line):
    """
    :param fdir:
    :param line:
    :return:
    """
    f = open(fdir, "a")
    f.write(line+"\n")
    f.close()


def annotate_t2dv2_ttla_meta(endpoint, remove_outliers):
    t2dv2_dir = 't2dv2'
    t2dv2_data_dir = os.path.join(data_dir, t2dv2_dir, 'data')
    meta_dir = os.path.join(data_dir, t2dv2_dir, 'meta.csv')
    df = pd.read_csv(meta_dir)
    # filename, concept, k, column, property, columnid, kind, sub_kind
    df = df[df.columnid.notnull()]
    ks = []
    for idx_out, row in df.iterrows():
        print("row: ")
        print(row)
        colid = int(row['columnid'])
        # fname = atts[0].strip()[1:-1]
        fname = row['filename'].strip()
        fname = fname[:-7] + ".csv"  # remove .tar.gz
        property_uri = row['property'].strip()
        class_uri = "http://dbpedia.org/ontology/"+row['concept'].strip()
        fdir = os.path.join(t2dv2_data_dir, fname)
        errs = annotate_a_col_in_file(fdir=fdir, class_uri=class_uri, endpoint=endpoint,
                               remove_outliers=remove_outliers, colid=colid)
        for idx, e in enumerate(errs[:3]):
            print("e1: "+e[1])
            line = ",".join([fname, class_uri, property_uri, fname_to_uri(e[1]), str(idx+1)])
            append_results("new_t2dv2_results.csv", line)
        k = get_k_from_errs(errs, property_uri)
        ks.append(k)
    compute_scores(ks)

# def annotate_t2dv2(endpoint, remove_outliers):
#     t2dv2_dir = 't2dv2'
#     t2dv2_data_dir = os.path.join(data_dir, t2dv2_dir, 'data')
#     meta_dir = os.path.join(data_dir, t2dv2_dir, 'meta.csv')
#     f = open(meta_dir)
#     ks = []
#     for line in f.readlines()[1:]:
#         atts = line.strip().split(',')
#         if len(atts) > 5:
#             print(atts)
#             colid = atts[5]
#             if colid.strip() != '':
#                 print("colid: "+colid)
#                 colid = int(colid)
#                 # fname = atts[0].strip()[1:-1]
#                 fname = atts[0].strip()
#                 fname = fname[:-7] + ".csv"  # remove .tar.gz
#                 property_uri = atts[4].strip()
#                 # class_uri = atts[2].strip()[1:-1]
#                 class_uri = "http://dbpedia.org/ontology/"+atts[1].strip()
#                 fdir = os.path.join(t2dv2_data_dir, fname)
#                 errs = annotate_a_col_in_file(fdir=fdir, class_uri=class_uri, endpoint=endpoint,
#                                        remove_outliers=remove_outliers, colid=colid)
#                 for idx, e in enumerate(errs[:3]):
#                     print("e1: "+e[1])
#                     line = ",".join([fname, class_uri, property_uri, fname_to_uri(e[1]), str(idx+1)])
#                     append_results("new_t2dv2_results.csv", line)
#                 k = get_k_from_errs(errs, property_uri)
#                 ks.append(k)
#                 # break
#                 # collect_numeric_data(class_uri=class_uri, endpoint=endpoint)
#                 # class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
#                 # properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
#                 # properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]
#                 # col = get_column(fdir, colid)
#                 # annotate_column(col=col, properties_dirs=properties_dirs, remove_outliers=remove_outliers)
#                 # annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, endpoint=endpoint)
#     compute_scores(ks)


a = datetime.now()

annotate_t2dv2_ttla_meta(endpoint='https://en-dbpedia.oeg.fi.upm.es/sparql', remove_outliers=True)
# annotate_olympic_games(endpoint='https://en-dbpedia.oeg.fi.upm.es/sparql', remove_outliers=True)


b = datetime.now()

print("Time it took")
print(b-a)
print((b-a).total_seconds())
print((b-a).total_seconds()/60.0)

# cols = get_numeric_columns('local_data/olympic_games/data/aaagolfplayers.csv')
# for col in cols:
#     print("\n\n\nColumn: ")
#     print(col)

# DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
# basketball_player_uri = "http://dbpedia.org/ontology/BasketballPlayer"
# collect_numeric_data(basketball_player_uri, DBPEDIA_ENDPOINT)
# aaa()

# errs = get_candidate_properties('http://dbpedia.org/ontology/BasketballPlayer',
#                                 get_data("local_olympic_basketball_height_cm.txt"))
#
# for e in errs:
#     print("%.4f\t %s" % (e[0], e[1]))

# DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
#
# basketball_player_uri = "http://dbpedia.org/ontology/BasketballPlayer"
# subjects = get_subjects(basketball_player_uri, DBPEDIA_ENDPOINT)
# logger.debug("Testing")
# collect_numeric_data(basketball_player_uri, DBPEDIA_ENDPOINT)