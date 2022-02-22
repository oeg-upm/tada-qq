from experiments.t2dv2 import *
from experiments.common import collect_numeric_data, get_columns_data

from qq.qqe import QQE
from qq.dist import get_data


def debug(endpoint, fname, col_id, class_uri, properties, remove_outliers, err_meth):
    """
    """
    fdir = os.path.join(data_dir, fname)
    collect_numeric_data(class_uri=class_uri, endpoint=endpoint, data_dir=data_dir, min_objs=MIN_NUM_OBJ)
    num_cols = get_columns_data(fdir, [col_id])
    class_dir = os.path.join(data_dir, uri_to_fname(class_uri))
    # properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
    # properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]

    target_properties_fnames = [uri_to_fname(p)+".txt" for p in properties]
    target_properties_files = [f for f in target_properties_fnames if os.path.isfile(os.path.join(class_dir, f))]
    target_properties_dirs = [os.path.join(class_dir, pf) for pf in target_properties_files]

    _, col = num_cols[0]

    qqe = QQE(col)
    errs = []
    print(target_properties_fnames)
    print(target_properties_dirs)
    for prop_f in target_properties_dirs:
        objects = get_data(prop_f)
        err = qqe.predict_and_get_error(objects, method=err_meth, remove_outliers=remove_outliers)
        item = (err, prop_f)
        errs.append(item)
    errs.sort()
    for e in errs:
        print("%.2f - %s" % (e[0], e[1]))
    return errs


if __name__ == '__main__':
    err_meth = "mean_err"
    concept = "Mountain"
    class_uri = 'http://dbpedia.org/ontology/%s' % concept
    fname = "1146722_1_7558140036342906956.tar.gz.csv"
    col_id = 6
    properties = [
        "http://dbpedia.org/ontology/prominence",
        "http://dbpedia.org/property/elevationM"
    ]
    debug(SPARQL_ENDPOINT, fname, col_id, class_uri, properties, True, err_meth)
