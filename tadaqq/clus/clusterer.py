from collections import Counter
from tadaqq.qq import QQE


class Clusterer:

    def __init__(self, save_memory=True):
        self.groups = []
        self.save_memory = save_memory

    def column_group_matching(self, ele, fetch_method, err_meth, err_cutoff, same_class):
        """
        Add column to one of the groups (or to a new group)
        """
        groups = self.groups
        min_idx = None
        min_err = 1
        qq = QQE(list(ele["col"]))
        for idx, g in enumerate(self.groups):
            if not g:
                print("group None")
                raise Exception("group is None")
            top_ele = g[0]
            if top_ele is None:
                raise Exception("top_ele is None")
            err = qq.predict_and_get_error(top_ele["col"], method=err_meth, remove_outliers=False)
            if err < min_err:
                if same_class and top_ele["concept"] != ele["concept"]:
                    continue
                min_idx = idx
                min_err = err

        if min_err < err_cutoff:
            group = self.add_col_to_group(ele, groups[min_idx], fetch_method)
            groups[min_idx] = group
        else:
            groups.append([ele])
        if groups[-1] is None:
            print(ele)
            raise Exception("column_group_matching> Exception: no groups is added")

    def add_col_to_group(self, ele, group, fetch_method):
        """
        Add ele to group.
        """
        if fetch_method == "max":
            if group[0]["num"] < ele["num"]:
                group.append(group[0])
                if self.save_memory:
                    group[-1]["col"] = []
                group[0] = ele
            else:
                if self.save_memory:
                    ele["col"] = []
                group.append(ele)
        elif fetch_method == "min":
            if group[0]["num"] > ele["num"]:
                group.append(group[0])
                group[-1]["col"] = []
                group[0] = ele
            else:
                if self.save_memory:
                    ele["col"] = []
                group.append(ele)
        else:
            raise Exception("add_col_to_group> Exception: unknown fetch method")
        return group

    def evaluate(self, counts, print_eval=False):
        """
        groups: [[{}], [{}]]
        counts: Counter of cluster values. Each value = "idx-concept-shot_property"
        """
        if print_eval:
            print("\n\nEVALUATE\n==============\n")
        max_per_v = dict()
        groups = self.groups
        for idx, g in enumerate(groups):
            vals = [ele['gs_clus'] for ele in g]
            c = Counter(vals)
            for k in c:
                prec = c[k] / len(vals)
                if k in max_per_v:
                    if (c[k] > max_per_v[k]['num']) or (c[k] == max_per_v[k]['num'] and prec > max_per_v[k]['prec']):
                        max_per_v[k] = {
                            'num': c[k],
                            'prec': prec,
                            'clus_id': idx
                        }
                else:
                    max_per_v[k] = {
                        'num': c[k],
                        'prec': prec,
                        'clus_id': idx
                    }

        scores = dict()
        precs = []
        recs = []
        f1s = []
        if print_eval:
            print("{:<35} {:<5} {:<5} {:<5} {:<5}".format("name", "prec", "rec", "f1", "clus"))
        for k in max_per_v:
            prec = max_per_v[k]['prec']
            rec = max_per_v[k]['num'] / counts[k]
            f1 = 2 * prec * rec / (prec + rec)
            scores[k] = {'prec': prec, 'rec': rec, 'f1': f1}
            precs.append(prec)
            recs.append(rec)
            f1s.append(f1)
            if print_eval:
                print("{:<35} {:<5} {:<5} {:<5} {:<5}".format(k, round(prec, 3), round(rec, 3), round(f1, 3),
                                                              max_per_v[k]['clus_id']))
        p, r, f = sum(precs) / len(precs), sum(recs) / len(recs), sum(f1s) / len(f1s)
        if print_eval:
            print("Average: Precision (%.3f), Recall (%.3f), F1 (%.3f)" % (p, r, f))
        return p, r, f


