from tadaqq.slabel import SLabel
from collections import Counter
from tadaqq.util import uri_to_fname, compute_scores


class SLabMer:

    def __init__(self, endpoint):
        self.sl = SLabel(endpoint)

    def annotate_cluster(self, group, remove_outliers, estimate, err_meth, candidate_failback, k=3):
        """
        Store the predicted properties and assign a single candidate for each element in the given group
        :param group:
        :param remove_outliers:
        :param estimate:
        :param err_meth:
        :param k:
        :return:
        """
        pred_classes = []
        for ele in group:
            pred = self.sl.annotate_column(ele['col'], class_uri=ele['class_uri'], remove_outliers=remove_outliers,
                                           estimate=estimate, err_meth=err_meth)
            pred = pred[:k]
            ele['preds'] = [perr[1] for perr in pred]
            # print("preds: ")
            # print(ele['preds'])
            for p in ele['preds']:
                pred_classes.append(p)
        c = Counter(pred_classes)
        freqs = c.most_common()

        for ele in group:
            # print("\nfreqs:")
            # print(freqs)
            for prop_uri, fre in freqs:
                if prop_uri in ele['preds']:
                    ele['candidate'] = prop_uri
                    # print("candidate found: %s" % prop_uri)
                    # print("properties: %s" % str(ele['properties']))
                    break
                # else:
                #     print("\n\nNo candidate found")
                #     print(prop_uri)
            if 'candidate' not in ele and candidate_failback:
                if len(ele['preds']) > 0:
                    ele['candidate'] = ele['preds'][0]
            if 'candidate' not in ele:
                ele['candidate'] = ''

    def annotate_clusters(self, groups, remove_outliers, estimate, err_meth, candidate_failback, k=3):
        for g in groups:
            self.annotate_cluster(g, remove_outliers, estimate, err_meth, candidate_failback, k)

    def evaluate_labelling(self, groups):
        """
        :param groups: list of groups. Each group is an ele
        :return:
        """
        eval_data = []
        for group in groups:
            for ele in group:
                corr_trans_uris = [uri_to_fname(p) for p in ele['properties']]
                res = self.sl.eval_column([(0.0, ele['candidate'])], correct_uris=corr_trans_uris, print_diff=False)
                eval_data.append(res)

        prec, rec, f1 = compute_scores(eval_data, k=1)
        score = {'prec': prec, 'rec': rec, 'f1': f1}
        return score

