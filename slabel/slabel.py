import os
import logging
from easysparql import easysparqlclass
from slabel import util
from qq.qqe import QQE
from qq.util import get_data

import pcake


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    # formatter = logging.Formatter('%(name)-12s>>  %(message)s')
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


class SLabel:

    def __init__(self, endpoint=None, cache_dir=".cache", logger=None, min_num_objs=30,
                 offline_data_dir="local_data"):
        self.esparql = easysparqlclass.EasySparql(cache_dir=cache_dir, logger=logger)
        if not logger:
            logger = get_logger(__name__, level=logging.INFO)
        self.logger = logger
        if endpoint:
            self.esparql.endpoint = endpoint
        self.offline_data_dir = offline_data_dir
        self.min_num_objs = min_num_objs

    def set_endpoint(self, endpoint):
        self.esparql.endpoint = endpoint

    def collect_numeric_data(self, class_uri):
        """
        :param class_uri:
        :return:
        """

        data_dir = self.offline_data_dir
        min_objs = self.min_num_objs

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

        util.create_dir(data_dir)
        class_dir = os.path.join(data_dir, util.uri_to_fname(class_uri))

        if os.path.exists(class_dir):
            return
        util.create_dir(class_dir)
        print("prop query: ")
        print(prop_query)
        results = self.esparql.run_query(prop_query)
        properties = [r['p']['value'] for r in results]

        for prop in properties:
            if util.data_exists(data_dir=data_dir, class_uri=class_uri, property_uri=prop):
                continue
            query = query_template % (class_uri, prop)
            results = self.esparql.run_query(query=query)

            if results is None:
                self.logger.debug('No results for the query: ' + query)
                continue

            objects = [r['o']['value'] for r in results]

            if len(objects) >= min_objs:
                nums = self.esparql.get_numerics_from_list(objects, 0.5)
                if nums is None:
                    self.logger.debug('property is not numeric: ' + prop)
                    continue
                elif len(nums) >= min_objs:
                    self.logger.debug('saving property: ' + prop)
                    util.save_objects(data_dir, class_uri, prop, nums)
                else:
                    self.logger.debug("less than 30 numeric values: " + prop)
            else:
                self.logger.debug('less than 30 objects: ' + prop)

    def annotate_column(self, col, class_uri=None, properties_dirs=[], remove_outliers=False, estimate=True, err_meth="mean_err"):
        """
        col:
        class_uri:
        properties_dirs:
        remove_outliers:
        err_meth
        """
        if not properties_dirs:
            if not class_uri:
                err_msg = "You should either pass the class uri or the properties_dirs"
                self.logger.error(err_msg)
                print(err_msg)
                raise Exception(err_msg)
            else:
                class_dir = os.path.join(self.offline_data_dir, util.uri_to_fname(class_uri))
                properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
                properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]

        qqe = QQE(col, estimate_quantile=estimate, remove_outliers=remove_outliers)
        errs = []
        for prop_f in properties_dirs:
            objects = get_data(prop_f)
            err = qqe.predict_and_get_error(objects, method=err_meth, remove_outliers=remove_outliers)
            item = (err, prop_f)
            errs.append(item)
        errs.sort()
        return errs

    def annotate_file(self, fdir, class_uri, remove_outliers, cols=[], estimate=True, err_meth="mean_err",
                      print_diff=False):
        """
        :param fdir: of the csv file to be annotated
        :param class_uri:
        :param remove_outliers: True/False
        :param cols: list of int - the ids of the numeric columns. If nothing is passed, the function will detect
        numeric columns
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
        self.collect_numeric_data(class_uri=class_uri)
        if not cols:
            num_cols = self.get_numeric_columns(fdir)
        else:
            num_cols = util.get_columns_data(fdir, cols)
        class_dir = os.path.join(self.offline_data_dir, util.uri_to_fname(class_uri))
        properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
        properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]
        preds = dict()
        if print_diff:
            print("\n\n=================")
            print(class_uri)
            print(fdir)
        self.logger.debug("\n\n=================")
        self.logger.debug(class_uri)
        self.logger.debug(fdir)
        for colobj in num_cols:
            colid, coldata = colobj
            # logger.info('\n\n%s - (col=%d) ' % (fdir.split('/')[-1], colid))
            if print_diff:
                print('Column: ' + str(colid))
                print("annotate_column")
            self.logger.debug('Column: ' + str(colid))
            self.logger.debug("annotate_column")
            errs = self.annotate_column(col=coldata, properties_dirs=properties_dirs, remove_outliers=remove_outliers,
                                   err_meth=err_meth, estimate=estimate)
            preds[colid] = errs
        return preds

    def eval_column(self, p_errs, correct_uris=[], diff_diagram=None, class_uri=None, col_id=None, fdir=None,
                    print_diff=False):
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
            trans_uri = util.uri_to_fname(trans_uri)
            if trans_uri in correct_uris:
                k = idx + 1
                if print_diff:
                    print("Match: %.2f - <%s> - <%s>" % (item[0], trans_uri, util.property_dir_to_uri(item[1])[1]))
                if idx > 0:
                    if diff_diagram:
                        data = util.get_columns_data(fdir, [col_id])[0][1]
                        prev_property_uri = util.property_dir_to_uri(p_errs[idx - 1][1])[1]
                        if print_diff:
                            print("property dir to uri:")
                            print(item[1])
                        pcake.compare(class_uri, util.property_dir_to_uri(item[1])[1], prev_property_uri,
                                      label1a=" (correct)",
                                      label2a=" (incorrect)", data=data, data_label="data", outfile=diff_diagram)
                break
            elif idx < 3:
                if idx == 0:
                    if print_diff:
                        print("Correct uris: %s \t" % str(correct_uris))
                if print_diff:
                    print("%d err: %.2f - <%s> - <%s>" % (idx + 1, item[0], trans_uri, util.property_dir_to_uri(item[1])[1]))
            else:
                k = 999
                data = util.get_columns_data(fdir, [col_id])[0][1]
                prev_property_uri = util.property_dir_to_uri(p_errs[0][1])[1]
                base_a = os.sep.join(p_errs[0][1].split(os.sep)[:-1])
                corr_uri = os.path.join(base_a, correct_uris[0] + ".txt")
                if print_diff:
                    print("property dir to uri: ***")
                    print(corr_uri)
                try:
                    if diff_diagram:
                        pcake.compare(class_uri, util.property_dir_to_uri(corr_uri)[1], prev_property_uri,
                                      label1a=" (correct*)",
                                      label2a=" (incorrect)", data=data, data_label="data", outfile=diff_diagram)
                except:
                    pass
                break
        return k

