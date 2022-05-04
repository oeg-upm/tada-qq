from tadaqq.slabel import SLabel
from collections import Counter
from tadaqq.util import uri_to_fname, compute_scores


class SLabMer:

    SLAB_PREF = 'slabel_pref'
    CLUS_PREF = 'clus_pref'
    PREFS = [SLAB_PREF, CLUS_PREF]

    def __init__(self, endpoint):
        self.sl = SLabel(endpoint)

    def _assign_preds_and_get_freq(self, group, remove_outliers, estimate, err_meth, k=3):
        pred_classes = []
        for ele in group:
            self.sl.collect_numeric_data(class_uri=ele['class_uri'])
            pred = self.sl.annotate_column(ele['col'], class_uri=ele['class_uri'], remove_outliers=remove_outliers,
                                           estimate=estimate, err_meth=err_meth)
            pred = pred[:k]
            ele['preds'] = [perr[1] for perr in pred]
            ele['candidates'] = []
            for p in ele['preds']:
                pred_classes.append(p)

        c = Counter(pred_classes)
        freqs = c.most_common()
        return freqs

    def annotate_cluster(self, group, remove_outliers, estimate, err_meth, candidate_failback, pref=None, k=3):
        """
        Store the predicted properties and assign a single candidate for each element in the given group
        :param group:
        :param remove_outliers:
        :param estimate:
        :param err_meth:
        :param k:
        :return:
        """
        if pref not in self.PREFS:
            print("Invalid preference")
            return None

        freqs = self._assign_preds_and_get_freq(group=group, remove_outliers=remove_outliers, estimate=estimate,
                                                     err_meth=err_meth, k=k)
        if pref == self.SLAB_PREF:
            return self.annotate_cluster_slabel_pref(group=group, freqs=freqs, candidate_failback=candidate_failback)
        elif pref == self.CLUS_PREF:
            return self.annotate_cluster_clus_pref(group=group, freqs=freqs)

    def annotate_cluster_clus_pref(self, group, freqs):
        """
        Store the predicted properties and assign a single candidate for each element in the given group

        :param group:
        :param freqs: a list of the pairs (property uri, number of occurrences)
        :return:
        """
        # print("\n\nGroup: ")
        for ele in group:
            for prop_uri, fre in freqs:
                ele['candidates'].append(prop_uri)

            # print("\tclass uri: %s" % ele['class_uri'])
            # print("\tcol id: %d" % ele['col_id'])
            # print("\tfname: %s" % ele['fname'])
            # print("\tproperty: %s " % ele['property'])
            # print("\tcandidate: %s " % str(ele['candidates'][:3]))
            # print("===============================")

    def annotate_cluster_slabel_pref(self, group, freqs, candidate_failback):
        """
        Store the predicted properties and assign a single candidate for each element in the given group
        :param group:
        :param remove_outliers:
        :param estimate:
        :param err_meth:
        :param k:
        :return:
        """

        # print("\n\nGroup: ")
        for ele in group:
            for prop_uri, fre in freqs:
                if prop_uri in ele['preds']:
                    ele['candidates'].append(prop_uri)

            # print("\tclass uri: %s" % ele['class_uri'])
            # print("\tcol id: %d" % ele['col_id'])
            # print("\tfname: %s" % ele['fname'])
            # print("\tproperty: %s " % ele['property'])
            # print("\tcandidate: %s " % str(ele['candidates'][:3]))
            # print("===============================")

            if candidate_failback:
                for p in ele['preds']:
                    if p not in ele['candidates']:
                        ele['candidates'].append(p)

    def annotate_clusters(self, groups, remove_outliers, estimate, err_meth, candidate_failback, pref=SLAB_PREF, k=3):
        for g in groups:
            self.annotate_cluster(group=g, remove_outliers=remove_outliers, estimate=estimate, err_meth=err_meth,
                                  candidate_failback=candidate_failback, k=k, pref=pref)

    def evaluate_labelling(self, groups):
        """
        :param groups: list of groups. Each group is an ele
        :return:
        """
        eval_data = []
        for group in groups:
            for ele in group:
                corr_trans_uris = [uri_to_fname(p) for p in ele['properties']]
                p_errs = [(0.0, cand) for cand in ele['candidates']]
                res = self.sl.eval_column(p_errs, correct_uris=corr_trans_uris, print_diff=False)
                eval_data.append(res)
        prec, rec, f1 = compute_scores(eval_data, k=1)
        score = {'prec': prec, 'rec': rec, 'f1': f1}
        return score


