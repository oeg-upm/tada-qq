import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from qq.qqe import QQE
from qq.util import errors_mean


class QQE2(QQE):

    def compute_and_draw_with_range(self, sample, mult, b):
        # qqe = QQE(a)
        # base_quantiles = qqe.estimated_base_eq
        # predicted_quantiles = qqe.estimate_sample_quantiles(b)
        # adjusted_quantiles = qqe.get_adjusted_base_quantiles(len(predicted_quantiles))

        predicted_quantiles = self.estimate_sample_quantiles(sample)
        y = predicted_quantiles
        x = self.get_adjusted_base_quantiles(len(predicted_quantiles))

        # Change the x and y to another range
        x = [xx * mult - b for xx in x]
        y = [yy * mult - b for yy in y]
        print("New X: ")
        print(x)

        err = errors_mean(y, x)
        print("errors mean: "+str(err))
        df = pd.DataFrame(zip(x, y), columns=["x", "y"])
        # print(df)
        # sns.lmplot(x="x", y="y", data=df)
        ax = sns.scatterplot(x="x", y="y", data=df, linewidth=0.05)
        ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([-b, b], [-b, b]), columns=["x", "y"]), ax=ax)
        plt.savefig('fig.eps', format='eps')
        plt.show()

    def compute_and_draw(self, sample):
        # qqe = QQE(a)
        # base_quantiles = qqe.estimated_base_eq
        # predicted_quantiles = qqe.estimate_sample_quantiles(b)
        # adjusted_quantiles = qqe.get_adjusted_base_quantiles(len(predicted_quantiles))

        predicted_quantiles = self.estimate_sample_quantiles(sample)
        y = predicted_quantiles
        x = self.get_adjusted_base_quantiles(len(predicted_quantiles))

        err = errors_mean(y, x)
        print("errors mean: "+str(err))
        df = pd.DataFrame(zip(x, y), columns=["x", "y"])
        # print(df)
        # sns.lmplot(x="x", y="y", data=df)
        ax = sns.scatterplot(x="x", y="y", data=df, linewidth=0.05)
        ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([0, 1], [0, 1]), columns=["x", "y"]), ax=ax)
        #plt.savefig('fig.eps', format='eps')
        plt.show()

# def f():
#     sample_data = [2,1,3.4,-2,-1.1]
#     sample_data.sort()
#
#
# def estimate_base_quantiles(sorted_data):
#     """
#     :param sorted_data:
#     :return:
#     """
#     n = len(sorted_data) * 1.0
#     eq = []  # estimated quantiles
#     for i0, d in enumerate(sorted_data):
#         i = i0+1  # as the formula starts from i = 1
#         q = (i-0.5)/n
#         print(q)
#         eq.append(q)
#     return eq


# class QQE(object):
#     """
#     This is the quantile-quantile estimator
#     """
#
#     def __init__(self, sample_data):
#         self.sample_base = sample_data
#         self.sample_base = self._remove_duplicates(self.sample_base)
#         self.sample_base.sort()
#         self.estimated_base_eq = self._estimate_base_quantiles(self.sample_base)
#         self.ms = self._compute_ms(self.sample_base, self.estimated_base_eq)
#         self.bs = self._compute_bs(self.sample_base, self.estimated_base_eq, self.ms)  # estimate the b shift
#
#     def _remove_duplicates(self, data):
#         return list(set(data))
#
#     def _estimate_base_quantiles(self, sorted_data):
#         """
#         :param sorted_data:
#         :return:
#         """
#         n = len(sorted_data) * 1.0
#         eq = []  # estimated quantiles
#         print("Estimated base: ")
#         for i0, d in enumerate(sorted_data):
#             i = i0 + 1  # as the formula starts from i = 1
#             q = (i - 0.5) / n
#             # print("x = %2.2f    y = %2.2f   " % (d, q))
#             #print(q)
#             eq.append(q)
#         return eq
#
#     def estimate_sample_quantiles(self, data):
#         """
#         :param data:
#         :return:
#         """
#         predicted_quantiles = []
#         clean_data = self._remove_duplicates(data)
#         print("\nPredicted quantiles: ")
#         for d in sorted(clean_data):
#             y = self.estimate_datum_quantile(d)
#             # print("x = %2.2f    y = %2.2f" % (d, y))
#             #print(y)
#             predicted_quantiles.append(y)
#         return predicted_quantiles
#
#     def estimate_datum_quantile(self, data_point):
#         """
#         :param data_point: float
#         :return: quantile: float
#         """
#         # set quantile for quantile > (n-0.5)/n
#         m = self.ms[-1]
#         b = self.bs[-1]
#         # For quantile < (0.5)/n
#         if data_point < self.sample_base[0]:
#             m = self.ms[0]
#             b = self.bs[0]
#         else:  # for 0.5/n < quantile < (n-0.5)/n
#             for i, d in enumerate(self.sample_base[1:]):
#                 if data_point < d:
#                     m = self.ms[i]
#                     b = self.bs[i]
#                     break
#
#         y = data_point * m + b
#         y = max(0.0, y)
#         y = min(y, 1.0)
#         return y
#
#     def get_adjusted_base_quantiles(self, n):
#         """
#         :param n: the required number of quantiles
#         :return:
#         """
#         aq = []
#         for i in range(1, n+1):
#             aq.append((i-0.5)/n)
#             #aq.append(i*1.0/n)
#         return aq
#
#     def _compute_ms(self, sample_data, quantiles):
#         """
#         :param sample_data:
#         :param quantiles:
#         :return:
#         """
#         # data_quantile_pairs = zip(sample_data, quantiles)
#         ms = []
#         print("\nslopes: ")
#         for i in range(0, len(sample_data)-1):
#             x1 = sample_data[i]
#             x2 = sample_data[i+1]
#             y1 = quantiles[i]
#             y2 = quantiles[i+1]
#             dx = (x2 - x1)
#             dy = (y2 - y1)
#             #m = (y2 - y1) / (x2 - x1)
#             if dx == 0:
#                 print("error: "+str(x2))
#                 m = (y2 - y1) / (x2 - x1)
#             else:
#                 m = dy / dx
#             # print("m = %2.2f    x1 = %2.2f   x2 = %2.2f  y1 = %2.2f  y2 = %2.2f" % (m, x1, x2, y1, y2))
#             # print(m)
#             ms.append(m)
#         return ms
#
#     def _compute_bs(self, sample_data, quantiles, slopes):
#         """
#         y = mx + b
#         compute the b shift for the linear equation
#         :param sample_data:
#         :param quantiles:
#         :param slopes:
#         :return:
#         """
#         bs = []
#         for i in range(0, len(sample_data)-1):
#             b = quantiles[i] - slopes[i] * sample_data[i]
#             bs.append(b)
#         return bs
#
#     def compute_and_draw(self, sample):
#         import pandas as pd
#         import matplotlib
#         matplotlib.use('TkAgg')
#         import matplotlib.pyplot as plt
#         import seaborn as sns
#
#         # qqe = QQE(a)
#         # base_quantiles = qqe.estimated_base_eq
#         # predicted_quantiles = qqe.estimate_sample_quantiles(b)
#         # adjusted_quantiles = qqe.get_adjusted_base_quantiles(len(predicted_quantiles))
#
#         predicted_quantiles = self.estimate_sample_quantiles(sample)
#         y = predicted_quantiles
#         x = self.get_adjusted_base_quantiles(len(predicted_quantiles))
#         err_sq = mean_squared_error(x,y)
#         print("squared error: "+str(err_sq))
#         err = mean_errors(y,x)
#         print("errors mean: "+str(err))
#         df = pd.DataFrame(zip(x, y), columns=["x", "y"])
#         # print(df)
#         # sns.lmplot(x="x", y="y", data=df)
#         ax = sns.scatterplot(x="x", y="y", data=df, linewidth=0.05)
#         ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([0, 1], [0, 1]), columns=["x", "y"]), ax=ax)
#         # plt.savefig('fig.eps', format='eps')
#         plt.show()


# def errors_mean(y_pred, y_real):
#     """
#     :param y_pred:
#     :param y_real:
#     :return:
#     """
#     if len(y_pred) != len(y_real):
#         print("Error, unmatched number of ys")
#         return None
#     tot_err = 0.0
#     for i in range(len(y_pred)):
#         tot_err += abs(y_pred[i]-y_real[i])
#     mean_tot_err = tot_err/len(y_pred)
#     print("total error: "+str(tot_err))
#     print("mean error: "+str(mean_tot_err))
#     return mean_tot_err


def draw(x, y):
    df = pd.DataFrame(zip(x,y), columns=["x","y"])
    # print(df)
    # sns.lmplot(x="x", y="y", data=df)
    ax = sns.scatterplot(x="x", y="y", data=df, linewidth=0.05)
    ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([0,1],[0,1]), columns=["x","y"]), ax=ax)
    # plt.savefig('fig.eps', format='eps')
    plt.show()


    # Example
    # import seaborn as sns
    # df = sns.load_dataset('iris')
    # # use the function regplot to make a scatterplot
    # sns.regplot(x=df["sepal_length"], y=df["sepal_width"])
    # # sns.plt.show()
    # # Without regression fit:
    # sns.regplot(x=df["sepal_length"], y=df["sepal_width"], fit_reg=False)

    # g = sns.scatterplot(x="x", y="y", data=df)
    # g = sns.FacetGrid(tips, row="sex", col="smoker", margin_titles=True, height=2.5)
    # g.map(plt.scatter, "total_bill", "tip", color="#334488", edgecolor="white", lw=.5);
    # g.set_axis_labels("Total bill (US Dollars)", "Tip");
    # g.set(xticks=[10, 30, 50], yticks=[2, 6, 10]);
    #g.fig.subplots_adjust(wspace=.02, hspace=.02)


# a = [
# -1.742228051,
# -0.917002581,
# -0.564285756,
# 0.012862529,
# 0.307192067,
# 0.324218945,
# 0.636133564,
# 0.755255769,
# 0.85051397,
# 1.308635547
# ]
#
# b = [
# -1.662046998,
# -0.685645318,
# -0.543952865,
# -0.274905005,
# -0.176792128,
# 0.708121206,
# 0.899674433,
# 1.056559995,
# 1.78746177,
# 2.67267751
# ]

def get_data(fname):
    """
    :param fname:
    :return:
    """
    a = []
    f = open(fname)
    for line in f.readlines():
        if line.strip() != "":
            a.append(float(line))
    f.close()
    return a


def get_stats(data):
    mean = np.mean(data)
    median = np.median(data)
    std = np.std(data)
    # print("mean: "+str(mean))
    # print("median: "+str(median))
    # print("std: "+str(std))
    return mean, median, std


def compare_stats(data1, data2):
    """
    :param data1:
    :param data2:
    :return:
    """
    mean1, median1, std1 = get_stats(data1)
    mean2, median2, std2 = get_stats(data2)
    print("%10s     %10s      %10s" % ("Mean", "Median", "STD"))
    print("%10f.2   %10f.2    %10f.2" % (mean1, median1, std1))
    print("%10f.2   %10f.2    %10f.2" % (mean2, median2, std2))


def run():

    # a = get_data("local_sample1_n1000.txt")
    # b = get_data("local_sample2_n1000.txt")
    # a = get_data("local_normal_n10000_m3_s2.txt")
    # b = get_data("local_normal_n10000_2.txt")
    a = get_data("local_dbpedia.org-ontology-Person-height - dbpedia.org-ontology-BasketballPlayer.txt")
    #b = get_data("local_dbpedia.org-ontology-Person-height - dbpedia.org-ontology-SoccerPlayer.txt")
    #b = get_data("local_dbpedia.org-ontology-Person-height - dbpedia.org-ontology-BasketballPlayer.txt")
    b = get_data("local_olympic_basketball_height_cm.txt")
    # get_stats(a)
    # get_stats(b)
    compare_stats(a, b)
    qqe = QQE2(a)
    # qqe.compute_and_draw(b)
    qqe.compute_and_draw_with_range(b, mult=5, b=2.5)

    # b = get_data("local_sample2_n1000.txt")
    # compare_stats(a, b)
    # qqe = QQE2(a)
    # qqe.compute_and_draw(b)


def sample_25():
    a = get_data("local_olympic_basketball_height_cm.txt")
    b = get_data("local_olympic_basketball_height_cm.txt")[10:30]
    b.append(320)
    # b.append(320.1)
    # b.append(320.22)
    b.append(310.3)
    b.append(290.32)
    b.append(220)
    b.append(230)
    b.append(240)
    b.append(170)
    b.append(172)
    b.append(173)
    # b.append(170.5)
    # b.append(172.5)
    # b.append(173.5)
    b.append(154.5)
    b.append(153.5)
    b.append(133.5)
    # b.append(170.25)
    # b.append(172.25)
    # b.append(173.25)

    qqe = QQE2(a)
    qqe.compute_and_draw_with_range(b, mult=5, b=2.5)


if __name__ == '__main__':
    sample_25()

