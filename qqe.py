from util import errors_mean
import numpy as np


class QQE(object):
    """
    This is the quantile-quantile estimator
    """

    def __init__(self, sample_data, remove_outliers=False):
        self.sample_base = sample_data
        self.sample_base = self._remove_duplicates(self.sample_base)
        self.sample_base.sort()
        self.sample_base = self.remove_outliers(self.sample_base)
        self.estimated_base_eq = self._estimate_base_quantiles(self.sample_base)
        self.ms = self._compute_ms(self.sample_base, self.estimated_base_eq)
        self.bs = self._compute_bs(self.sample_base, self.estimated_base_eq, self.ms)  # estimate the b shift

    def remove_outliers(self, sample):
        column = sample
        if len(column) < 1:
            return []
        clean_column = []
        q1 = np.percentile(column, 25)
        q3 = np.percentile(column, 75)
        # k = 1.5
        k = 2
        # [Q1 - k(Q3 - Q1), Q3 + k(Q3 - Q1)]
        lower_bound = q1 - k * (q3 - q1)
        upper_bound = q3 + k * (q3 - q1)
        for c in column:
            if c >= lower_bound and c <= upper_bound:
                clean_column.append(c)
        return clean_column

    def _remove_duplicates(self, data):
        return list(set(data))

    def _estimate_base_quantiles(self, sorted_data):
        """
        :param sorted_data:
        :return:
        """
        n = len(sorted_data) * 1.0
        eq = []  # estimated quantiles
        # print("Estimated base: ")
        for i0, d in enumerate(sorted_data):
            i = i0 + 1  # as the formula starts from i = 1
            q = (i - 0.5) / n
            # print("x = %2.2f    y = %2.2f   " % (d, q))
            #print(q)
            eq.append(q)
        return eq

    def estimate_sample_quantiles(self, data):
        """
        :param data:
        :return:
        """
        predicted_quantiles = []
        clean_data = self._remove_duplicates(data)
        # print("\nPredicted quantiles: ")
        for d in sorted(clean_data):
            y = self.estimate_datum_quantile(d)
            # print("x = %2.2f    y = %2.2f" % (d, y))
            #print(y)
            predicted_quantiles.append(y)
        return predicted_quantiles

    def estimate_datum_quantile(self, data_point):
        """
        :param data_point: float
        :return: quantile: float
        """
        # For quantile < (0.5)/n
        if data_point < self.sample_base[0]:
            m = self.ms[0]
            b = self.bs[0]
        # For quantile > (n-0.5)/n
        elif data_point > self.sample_base[-1]:
            m = self.ms[-1]
            b = self.bs[-1]
        else:  # for 0.5/n < quantile < (n-0.5)/n
            for i, d in enumerate(self.sample_base[1:]):
                if data_point <= d:
                    m = self.ms[i+1]
                    b = self.bs[i+1]
                    break

        y = data_point * m + b
        y = max(0.0, y)
        y = min(y, 1.0)
        return y

    def get_adjusted_base_quantiles(self, n):
        """
        :param n: the required number of quantiles
        :return:
        """
        aq = []
        for i in range(1, n+1):
            aq.append((i-0.5)/n)
            #aq.append(i*1.0/n)
        return aq

    def _compute_ms(self, sample_data, quantiles):
        """
        :param sample_data:
        :param quantiles:
        :return:
        """
        # data_quantile_pairs = zip(sample_data, quantiles)
        m = quantiles[0]/sample_data[0]
        ms = [m, ]
        # print("\nslopes: ")
        for i in range(0, len(sample_data)-1):
            x1 = sample_data[i]
            x2 = sample_data[i+1]
            y1 = quantiles[i]
            y2 = quantiles[i+1]
            dx = (x2 - x1)
            dy = (y2 - y1)
            #m = (y2 - y1) / (x2 - x1)
            if dx == 0:
                # logger.error("error: "+str(x2))
                print("error: "+str(x2))
                m = (y2 - y1) / (x2 - x1)
            else:
                m = dy / dx
            # print("m = %2.2f    x1 = %2.2f   x2 = %2.2f  y1 = %2.2f  y2 = %2.2f" % (m, x1, x2, y1, y2))
            # print(m)
            ms.append(m)
        ms.append(0)
        return ms

    def _compute_bs(self, sample_data, quantiles, slopes):
        """
        y = mx + b
        compute the b shift for the linear equation
        :param sample_data:
        :param quantiles:
        :param slopes:
        :return:
        """
        # qs = [0] + quantiles
        # bs = []
        # b = -sample_data[0] * slopes[0]  # for the first slope
        # bs = [b]
        # for i in range(0, len(sample_data)-1):
        #     b = qs[i] - slopes[i] * sample_data[i]
        #     bs.append(b)
        b = -sample_data[0] * slopes[0]  # for the first slope
        bs = [b]
        for i in range(0, len(sample_data)-1):
            b = quantiles[i] - slopes[i+1] * sample_data[i]
            bs.append(b)
        b = -sample_data[-1] * slopes[-1]  # for the last slope
        bs.append(b)
        return bs

    def compute_error_mean(self, sample, remove_outliers=True):
        if remove_outliers:
            clean_sample = self.remove_outliers(sample)
        else:
            clean_sample = sample
        predicted_quantiles = self.estimate_sample_quantiles(clean_sample)
        y = predicted_quantiles
        x = self.get_adjusted_base_quantiles(len(predicted_quantiles))
        err = errors_mean(y, x)
        # print("errors mean: " + str(err))
        return err