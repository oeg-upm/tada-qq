import os
import logging
from qqe import QQE
from easysparql import easysparql
from dist import get_data

data_dir = "local_data"


def get_logger(name, level=logging.INFO):
    # logging.basicConfig(level=level)
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__, level=logging.DEBUG)


def create_dir(adir):
    if not os.path.exists(adir):
        os.makedirs(adir)


def uri_to_fname(uri):
    fname = uri.strip().replace('http://','')
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


def save_objects(data_dir, class_uri, property_uri, objects):
    fdir = os.path.join(data_dir, uri_to_fname(class_uri), uri_to_fname(property_uri))
    # fname = uri_to_fname(class_uri) + " - " + uri_to_fname(property_uri)
    lines = [str(o) for o in objects]
    txt = "\n".join(lines)
    f = open(fdir, 'w')
    f.write(txt)
    f.close()


def data_exists(data_dir, class_uri, property_uri):
    fdir = os.path.join(data_dir, uri_to_fname(class_uri), uri_to_fname(property_uri))
    file_exists = os.path.exists(fdir)
    return file_exists


def collect_numeric_data(class_uri, endpoint):
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
    subjects = easysparql.get_subjects(class_uri=class_uri, endpoint=endpoint)
    logger.debug('num of subjects is: '+str(len(subjects)))
    total_num = len(subjects)
    for idx, subject in enumerate(subjects):
        logger.debug(" %d from %d" % (idx, total_num))
        properties = easysparql.get_properties_of_subject(subject_uri=subject, endpoint=endpoint)
        for prop in properties:
            if data_exists(data_dir=data_dir,class_uri=class_uri, property_uri=prop):
                continue
            query = query_template % (class_uri, prop)
            results = easysparql.run_query(query=query, endpoint=endpoint)
            if results is None:
                logger.debug('No results for the query: '+query)
                continue
            objects = [r['o']['value'] for r in results]
            if len(objects) >= 30:
                nums = easysparql.get_numerics_from_list(objects, 0.5)
                if nums is None:
                    logger.debug('property is not numeric: '+prop)
                    continue
                elif len(nums) >= 30:
                    logger.debug('saving property: '+prop)
                    save_objects(data_dir, class_uri, prop, nums)
                else:
                    logger.debug("less than 30 numeric values: "+prop)
            else:
                logger.debug('less than 30 objects: '+prop)

    # for each, get properties
    # for each, get count
    # check if numeric
    # for numerics, if count > 30, consider


def aaa():
    data_dir = 'local_data/dbo-BasketballPlayer'
    a = get_data("local_olympic_basketball_height_cm.txt")
    qqe = QQE(a)
    fnames = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    errs = []
    for fname in fnames:
        sample = get_data(os.path.join(data_dir, fname))
        err = qqe.compute_error_mean(sample, remove_outliers=True)
        print("mean: "+(str(err))+"  - "+fname)
        item = (err, fname)
        errs.append(item)

    errs.sort()
    for item in errs:
        print("err: "+str(item[0]) + "  - " + item[1])


DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
basketball_player_uri = "http://dbpedia.org/ontology/BasketballPlayer"
collect_numeric_data(basketball_player_uri, DBPEDIA_ENDPOINT)
aaa()
# DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
#
# basketball_player_uri = "http://dbpedia.org/ontology/BasketballPlayer"
# subjects = get_subjects(basketball_player_uri, DBPEDIA_ENDPOINT)
# logger.debug("Testing")
# collect_numeric_data(basketball_player_uri, DBPEDIA_ENDPOINT)