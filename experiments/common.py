import os
import logging

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from easysparql import easysparqlclass
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype

from pcake import pcake

from qq.qqe import QQE
from qq.dist import get_data

PRINT_DIFF = True


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(name)-12s>>  %(message)s')
    # formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__, level=logging.INFO)
# logger = get_logger(__name__, level=logging.DEBUG)
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


# def get_candidate_properties(class_uri, sample_data, data_dir):
#     """
#     :param class_uri:
#     :param sample_data:
#     :param data_dir:
#     :return: list of pairs. each pair os composed of (mean_err, prop-fname)
#     """
#     class_fname = uri_to_fname(class_uri)
#     class_dir = os.path.join(data_dir, class_fname)
#     qqe = QQE(sample_data)
#     fnames = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
#     errs = []
#     for f in fnames:
#         prop_dir = os.path.join(class_dir, f)
#         prop_data = get_data(prop_dir)
#         err = qqe.predict_and_get_mean_sq_error(prop_data, remove_outliers=True)
#         # err = qqe.predict_and_get_mean_error(prop_data, remove_outliers=True)
#         item = (err, f)
#         errs.append(item)
#
#     errs.sort()
#     return errs


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


def annotate_file(fdir, class_uri, endpoint, remove_outliers, data_dir, min_objs, cols=[], estimate=True,
                  err_meth="mean_err"):
    """
    :param fdir: of the csv file to be annotated
    :param class_uri:
    :param endpoint:
    :param remove_outliers: True/False
    :param data_dir:
    :param cols: list of int - the ids of the numeric columns. If nothing is passed, the function will detect
    numeric columns
    :param min_objs:
    :param err_meth:
    :param estimate: bool
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
    if PRINT_DIFF:
        print("\n\n=================")
        print(class_uri)
        print(fdir)
    for colobj in num_cols:
        colid, coldata = colobj
        # logger.info('\n\n%s - (col=%d) ' % (fdir.split('/')[-1], colid))
        if PRINT_DIFF:
            print('Column: ' + str(colid))
            print("annotate_column")
        errs = annotate_column(col=coldata, properties_dirs=properties_dirs, remove_outliers=remove_outliers,
                               err_meth=err_meth, estimate=estimate)
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


def annotate_column(col, properties_dirs, remove_outliers, estimate=True, err_meth="mean_err"):
    """
    col:
    properties_dirs:
    remove_outliers:
    err_meth
    """
    qqe = QQE(col, estimate_quantile=estimate, remove_outliers=remove_outliers)
    errs = []
    for prop_f in properties_dirs:
        objects = get_data(prop_f)
        err = qqe.predict_and_get_error(objects, method=err_meth, remove_outliers=remove_outliers)
        # if err_meth == "mean_err":
        #     err = qqe.predict_and_get_mean_error(objects, remove_outliers=remove_outliers)
        # elif err_meth == "mean_sq_err":
        #     err = qqe.predict_and_get_mean_sq_error(objects, remove_outliers=remove_outliers)
        # else:
        #     raise Exception("Unknown err_meth")
        item = (err, prop_f)
        errs.append(item)
    errs.sort()
    return errs


def property_dir_to_uri(fdir):
    class_name, prop_name = fdir.split(os.path.sep)[-2:]
    class_uri = fname_to_uri(class_name)
    property_uri = fname_to_uri(prop_name[:-4])
    return class_uri, property_uri


def eval_column(p_errs, correct_uris=[], diff_diagram=None, class_uri=None, col_id=None, fdir=None):
    """
    p_errs: a list of pairs. each pair starts with the error/distance and the filename
        (e.g., <0.1, dbo-Person-abc/dbp-xyz.txt>)
    correct_uris: a list of correct uris
    diff_diagram: the name of the output diagram showing the difference between the distributions
    The following parameters are only needed for the diff diagram
    class_uri:
    col_id:
    fdir:

    """
    k = -1
    if len(correct_uris) == 0:
        print("No correct uris as passed")
        print(p_errs)
        raise Exception("No correct uris are passed")
    for idx, item in enumerate(p_errs):
        trans_uri = item[1].split('/')[-1][:-4]
        trans_uri = uri_to_fname(trans_uri)
        if trans_uri in correct_uris:
            k = idx + 1
            if PRINT_DIFF:
                print("Match: %.2f - <%s> - <%s>" % (item[0], trans_uri, property_dir_to_uri(item[1])[1]))
            if idx > 0:
                if diff_diagram:
                    data = get_columns_data(fdir, [col_id])[0][1]
                    prev_property_uri = property_dir_to_uri(p_errs[idx-1][1])[1]
                    if PRINT_DIFF:
                        print("property dir to uri:")
                        print(item[1])
                    pcake.compare(class_uri, property_dir_to_uri(item[1])[1], prev_property_uri, label1a=" (correct)",
                                  label2a=" (incorrect)", data=data, data_label="data", outfile=diff_diagram)
            break
        elif idx < 3:
            if idx == 0:
                if PRINT_DIFF:
                    print("Correct uris: %s \t" % str(correct_uris))
            if PRINT_DIFF:
                print("%d err: %.2f - <%s> - <%s>" % (idx+1, item[0], trans_uri, property_dir_to_uri(item[1])[1]))
        else:
            k = 999
            data = get_columns_data(fdir, [col_id])[0][1]
            prev_property_uri = property_dir_to_uri(p_errs[0][1])[1]
            base_a = os.sep.join(p_errs[0][1].split(os.sep)[:-1])
            corr_uri = os.path.join(base_a, correct_uris[0]+".txt")
            if PRINT_DIFF:
                print("property dir to uri: ***")
                print(corr_uri)
            try:
                if diff_diagram:
                    pcake.compare(class_uri, property_dir_to_uri(corr_uri)[1], prev_property_uri, label1a=" (correct*)",
                                  label2a=" (incorrect)", data=data, data_label="data", outfile=diff_diagram)
            except:
                pass
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
            notf += 1
        elif d <= k:
            corr += 1
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
    # print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))


def get_num_rows(fdir):
    df = pd.read_csv(fdir)
    return len(df.index)


def compute_scores_per_key(eval_pp, fname=None, print_scores=False):
    """
    eval_pp: dict

    For example (property as a key)
    {
        "generic property": [1,... ] (k values),

    }
    """
    lines = []
    print("\n\n| %15s | %15s | %15s | %5s |" % ("Key", "Precision", "Recall", "F1"))
    print("|:%s:|:%s:|:%s:|:%s:|" % ("-"*15,"-"*15,"-"*15,"-"*5,))
    for p in eval_pp:
        prec, rec, f1 = compute_scores(eval_pp[p])
        lines.append([p, 'prec', prec])
        lines.append([p, 'rec', rec])
        lines.append([p, 'f1', f1])
        # if PRINT_DIFF:
        #     print("%s: \n\t%f1.2\t%f1.2\t%f1.2" % (p, prec, rec, f1))
        if print_scores:
            print("| %15s | %15.2f | %15.2f | %5.2f| " % (p, prec, rec, f1))

    if fname:
        generate_diagram(lines, fname)


def generate_diagram(acc, draw_fname):
    """
    :param acc: acc
    :param draw_file_base: base of the diagram
    :return: None
    """
    data = pd.DataFrame(acc, columns=['Property Concept', 'Metric', 'Value'])
    ax = sns.barplot(x="Value", y="Property Concept",
                     hue="Metric",
                     data=data, linewidth=1.0,
                     # palette="colorblind",
                     palette="Spectral",
                     # palette="pastel",
                     # palette="ch:start=.2,rot=-.3",
                     # palette="YlOrBr",
                     # palette="Paired",
                     # palette="Set2",
                     orient="h")
    # ax.legend_.remove()
    # ax.legend(bbox_to_anchor=(1.01, 1), borderaxespad=0)
    ax.legend(bbox_to_anchor=(1.0, -0.1), borderaxespad=0)
    # ax.set_xlim(0, 1.0)
    # ax.set_ylim(0, 0.7)
    # Horizontal
    ticks = ax.get_yticks()
    new_ticks = [t for t in ticks]
    texts = ax.get_yticklabels()
    # print(ax.get_yticklabels())
    labels = [t.get_text() for t in texts]
    ax.set_yticks(new_ticks)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set(xlabel=None, ylabel=None)
    # print(ax.get_yticklabels())
    plt.setp(ax.lines, color='k')
    ax.figure.savefig('%s.svg' % draw_fname, bbox_inches="tight")
    ax.figure.clf()


# def compute_counts(files_k, fname):
#     bins = [20, 30, 40, 50, 70, 100, 150, 200]
#     bins_acc = dict()
#     for f in files_k:
#         corr = 1
#         if files_k[f][0] != 1:
#             corr = 0
#         nrows = files_k[f][1]
#         added = False
#         for b in bins:
#             if nrows < b:
#                 bs = str(b)
#                 if bs not in bins_acc:
#                     bins_acc[bs] = []
#                 bins_acc[bs].append(corr)
#                 added = True
#         if not added:
#             bs = "%d<" % max(bins)
#             if bs not in bins_acc:
#                 bins_acc[bs] = []
#             bins_acc[bs].append(corr)
#     rows = []
#     for bname in bins_acc:
#         rows.append([bname, np.average(bins_acc[bname]), len(bins_acc[bname])])
#     df = pd.DataFrame(rows, columns=['nrows', 'accuracy', 'ncols'])
#     cats = [str(b) for b in bins] + ["%d<" % max(bins)]
#     x_pos = dict()
#     for idx, c in enumerate(cats):
#         x_pos[c] = idx
#     cat_type = CategoricalDtype(categories=cats, ordered=True)
#     df['nrows'] = df['nrows'].astype(cat_type)
#     print(df.dtypes)
#     print(df)
#
#     # p = sns.color_palette("flare", as_cmap=True)
#     # p = sns.color_palette("mako", as_cmap=True)
#     p = sns.dark_palette("#69d", reverse=False, as_cmap=True)
#
#     ax = sns.scatterplot(x="nrows", y="accuracy", data=df, size="ncols", hue="ncols",
#                          palette=p, sizes=(40, 100))
#     legend_labels, leg_oth = ax.get_legend_handles_labels()
#
#     sns.lineplot(data=df, x='nrows', y='accuracy', dashes=True, ax=ax, linestyle="--", linewidth=1, palette=p)
#     ax.legend(legend_labels, leg_oth, title="Number of columns")
#
#     # Draw number of files/columns
#     # for idx, row in df.iterrows():
#     #     nr = row['nrows']
#     #     nr = x_pos[nr]
#     #     plt.text(nr, row['accuracy'], row['ncols'])
#
#     ax.figure.savefig('%s.svg' % fname, bbox_inches="tight")
#     plt.show()
#     ax.figure.clf()
#


def compute_counts(files_k, fname):
    bins = [20, 30, 40, 50, 70, 100, 150, 200]
    bins_score = dict()
    for f in files_k:
        corr = 1
        if files_k[f][0] != 1:
            corr = 0
        nrows = files_k[f][1]
        added = False
        for b in bins:
            if nrows < b:
                bs = str(b)
                if bs not in bins_score:
                    bins_score[bs] = {
                        'corr': 0,
                        'notf': 0,
                        'incorr': 0
                    }
                if files_k[f][0] == 1:
                    bins_score[bs]['corr'] += 1
                elif files_k[f][0] == -1:
                    bins_score[bs]['notf'] += 1
                elif files_k[f][0] > 1:
                    bins_score[bs]['incorr'] += 1
                else:
                    raise Exception("Invalid k")
                added = True
        if not added:
            bs = "%d<" % max(bins)
            if bs not in bins_score:
                bins_score[bs] = {
                    'corr': 0,
                    'notf': 0,
                    'incorr': 0
                }
            if files_k[f][0] == 1:
                bins_score[bs]['corr'] += 1
            elif files_k[f][0] == -1:
                bins_score[bs]['notf'] += 1
            elif files_k[f][0] > 1:
                bins_score[bs]['incorr'] += 1
            else:
                raise Exception("Invalid k")

    rows = []
    for bname in bins_score:
        if bins_score[bname]['corr'] == 0:
            acc = 0
            prec = 0
            recall = 0
            f1 = 0
        else:
            acc = bins_score[bname]['corr'] / (bins_score[bname]['corr'] + bins_score[bname]['incorr'] + bins_score[bname]['notf'])
            prec = bins_score[bname]['corr'] / (bins_score[bname]['corr'] + bins_score[bname]['incorr'])
            recall = bins_score[bname]['corr'] / (bins_score[bname]['corr'] + bins_score[bname]['notf'])
            f1 = 2 * prec * recall / (prec+recall)
        tot = bins_score[bname]['corr'] + bins_score[bname]['incorr'] + bins_score[bname]['notf']
        rows.append([bname, acc, 'accuracy', tot])
        rows.append([bname, prec, 'precision', tot])
        rows.append([bname, recall, 'recall', tot])
        rows.append([bname, f1, 'f1', tot])

    #     rows.append([bname, acc, prec, recall, len(bins_score[bname])])
    # df = pd.DataFrame(rows, columns=['nrows', 'accuracy', 'precision', 'recall', 'ncols'])
    df = pd.DataFrame(rows, columns=['nrows', 'score', 'metric',  'ncols'])

    cats = [str(b) for b in bins] + ["%d<" % max(bins)]
    x_pos = dict()
    for idx, c in enumerate(cats):
        x_pos[c] = idx
    cat_type = CategoricalDtype(categories=cats, ordered=True)
    df['nrows'] = df['nrows'].astype(cat_type)

    cats = ['precision', 'recall', 'accuracy', 'f1']
    cat_type = CategoricalDtype(categories=cats)
    df['metric'] = df['metric'].astype(cat_type)
    # print(df.dtypes)
    # print(df)

    # p = sns.color_palette("flare", as_cmap=True)
    # p = sns.color_palette("mako", as_cmap=True)
    # p = sns.dark_palette("#69d", reverse=False, as_cmap=True)

    ax = sns.scatterplot(x="nrows", y="score", data=df, size="ncols", hue="metric",
                         #palette=p,
                         sizes=(40, 100))
    # legend_labels, leg_oth = ax.get_legend_handles_labels()
    # ax = sns.scatterplot(x="nrows", y="precision", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)
    # ax = sns.scatterplot(x="nrows", y="recall", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)

    # sns.lineplot(data=df, x='nrows', y='accuracy', dashes=True, ax=ax, linestyle="--", linewidth=1, palette=p)
    # sns.lineplot(data=df, x='nrows', y='score', dashes=True, ax=ax, linestyle="--", linewidth=1, hue="metric")
    linestyles = ["--", ":", "dashdot", "solid"]
    for idx, c in enumerate(cats):
        sns.lineplot(data=df[df.metric == c], x='nrows', y='score', dashes=True, ax=ax, linestyle=linestyles[idx], linewidth=1)

    # sns.move_legend(ax, "lower center", bbox_to_anchor=(.5, 0.5), ncol=2, title=None, frameon=False)
    # ax.set(ylim=(0, 1))
    ax.legend(loc=2, fontsize='x-small')

    # ax.legend(bbox_to_anchor=(0.1, 1.0), borderaxespad=0)
    # ax.legend(legend_labels, leg_oth, title="Number of columns")

    # Draw number of files/columns
    # for idx, row in df.iterrows():
    #     nr = row['nrows']
    #     nr = x_pos[nr]
    #     plt.text(nr, row['accuracy'], row['ncols'])

    ax.figure.savefig('%s.svg' % fname, bbox_inches="tight")
    # plt.show()
    ax.figure.clf()
    return df


def compute_counts_per_err_meth(scores_dict, fname):
    """
    scores_dict: dict
    {
        'estimate': {
            'mean_sq_err': df,
            'mean_err': df,
        },
        'exact': {}
    }

    sample df:
                nrows  score     metric  ncols
            0  200<      0   accuracy      1
            1  200<      0  precision      1
            2  200<      0     recall      1
            3  200<      0         f1      1
            4   200      0   accuracy      1
            5   200      0  precision      1
            6   200      0     recall      1
            7   200      0         f1      1
    """
    # df = pd.DataFrame()
    dfs = []
    for e in scores_dict:
        for m in scores_dict[e]:
            df1 = scores_dict[e][m]
            df1['pred'] = [e] * len(df1.index)
            df1['method'] = [m] * len(df1.index)
            # print("==============")
            # print(e)
            # print(m)
            # print(df1)
            # print("\n")
            dfs.append(df1)

    df = pd.concat(dfs, ignore_index=True)
    df = df[df.metric == "f1"]

    print("df: ")
    print(df)
    # p = sns.color_palette("flare", as_cmap=True)
    # p = sns.color_palette("mako", as_cmap=True)
    # p = sns.dark_palette("#69d", reverse=False, as_cmap=True)
    # p = "mako"
    # p = sns.color_palette(palette="mako", n_colors=2, desat=None, as_cmap=False)
    colors = ["#F26B38", "#2F9599"]
    p = sns.color_palette(palette=colors, n_colors=2, desat=None, as_cmap=True)

    ax = sns.scatterplot(x="nrows", y="score", data=df, hue="pred",
                         # size="ncols",
                         palette=p,
                         style="method")
                         # sizes=(40, 100))
    # legend_labels, leg_oth = ax.get_legend_handles_labels()
    # ax = sns.scatterplot(x="nrows", y="precision", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)
    # ax = sns.scatterplot(x="nrows", y="recall", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)


    # With Pred
    cats = ['estimate', 'exact']
    cat_type = CategoricalDtype(categories=cats)
    df['pred'] = df['pred'].astype(cat_type)
    # sns.lineplot(data=df, x='nrows', y='accuracy', dashes=True, ax=ax, linestyle="--", linewidth=1, palette=p)
    # sns.lineplot(data=df, x='nrows', y='score', dashes=True, ax=ax, linestyle="--", linewidth=1, hue="metric")
    linestyles = ["--",  ":", "dashdot", "solid"]
    # [".33", ".66"]

    for idx, c in enumerate(scores_dict):
        # print("cat: %s" % c)
        for m in scores_dict[e]:
            sns.lineplot(data=df[(df.pred == c) & (df.method == m)], x='nrows', y='score', dashes=True, ax=ax,
                         linestyle=linestyles[idx],
                         color=colors[idx],
                         #palette=p,
                         linewidth=2)

    # for idx, c in enumerate(cats):
    #     print("cat: %s" % c)
    #     sns.lineplot(data=df[df.pred == c], x='nrows', y='score', dashes=True, ax=ax, linestyle=linestyles[idx], linewidth=1)
    #     break

    # sns.move_legend(ax, "lower center", bbox_to_anchor=(.5, 0.5), ncol=2, title=None, frameon=False)
    # ax.set(ylim=(0, 1))
    ax.legend(loc=2, fontsize='x-small')

    # ax.legend(bbox_to_anchor=(0.1, 1.0), borderaxespad=0)
    # ax.legend(legend_labels, leg_oth, title="Number of columns")

    # Draw number of files/columns
    # for idx, row in df.iterrows():
    #     nr = row['nrows']
    #     nr = x_pos[nr]
    #     plt.text(nr, row['accuracy'], row['ncols'])

    ax.figure.savefig('%s.svg' % fname, bbox_inches="tight")
    # plt.show()
    ax.figure.clf()


def print_md_scores(scores):
    print("\n\n| %15s | %9s | %15s | %9s | %9s | %5s |" % (
    "remove outlier", "estimate", "error method", "Precision", "Recall", "F1"))
    print("|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 9, "-" * 9, "-" * 5))
    for sc in scores:
        ro, est, err_meth, prec, rec, f1 = sc['ro'], sc['est'], sc['err_meth'], sc['prec'], sc['rec'], sc['f1']
        if est:
            est_txt = "estimate"
        else:
            est_txt = "exact"
        ro_txt = str(ro)
        print("| %15s | %9s | %15s | %9.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, err_meth, prec, rec, f1))
