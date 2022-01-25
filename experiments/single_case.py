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

    target_properties_fnames = [uri_to_fname(p) for p in properties]
    target_properties_files = [f for f in target_properties_fnames if os.path.isfile(os.path.join(class_dir, f))]
    target_properties_dirs = [os.path.join(class_dir, pf) for pf in target_properties_files]

    _, col = num_cols[0]

    qqe = QQE(col)
    errs = []
    for prop_f in target_properties_dirs:
        objects = get_data(prop_f)
        if err_meth == "mean_err":
            err = qqe.predict_and_get_mean_error(objects, remove_outliers=remove_outliers)
        elif err_meth == "mean_sq_err":
            err = qqe.predict_and_get_mean_sq_error(objects, remove_outliers=remove_outliers)
        else:
            raise Exception("Unknown err_meth")
        item = (err, prop_f)
        errs.append(item)
    errs.sort()
    return errs


if __name__ == '__main__':
    err_meth = "mean_sq_err"
    class_uri = 'http://dbpedia.org/ontology/'
    fname = ""
    col_id = 0
    debug(SPARQL_ENDPOINT, fname, col_id, class_uri, True, err_meth)
