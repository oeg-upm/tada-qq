import unittest
import numpy as np
from qq.qqe import QQE


class QQTest(unittest.TestCase):

    # def test_qq_one_value(self):
    #     norm_data1 = [1]
    #     norm_data2 = [1]
    #     e = QQE(norm_data1, estimate_quantile=False)
    #     me = e.predict_and_get_error(norm_data2, method="mean_sq_err")
    #     # print("mean sq error: %f" % me)
    #     self.assertLess(me, 0.1)
    #     me = e.predict_and_get_error(norm_data2, method="mean_sq1_err")
    #     # print("mean sq1 error: %f" % me)
    #     self.assertLess(me, 0.1)

    def test_qq_same_dist_err_sq_and_1(self):
        norm_data1 = np.random.normal(size=200)
        norm_data2 = np.random.normal(size=200)
        e = QQE(norm_data1, estimate_quantile=True)
        me = e.predict_and_get_error(norm_data2, method="mean_sq_err")
        # print("mean sq error: %f" % me)
        self.assertLess(me, 0.1)
        me = e.predict_and_get_error(norm_data2, method="mean_sq1_err")
        # print("mean sq1 error: %f" % me)
        self.assertLess(me, 0.1)

    def test_qq_same_dist(self):
        norm_data1 = np.random.normal(size=200)
        norm_data2 = np.random.normal(size=200)
        e = QQE(norm_data1, estimate_quantile=True)
        me = e.predict_and_get_error(norm_data2, method="mean_err")
        # print("mean error: %f" % me)
        self.assertLess(me, 0.1)

    def test_qq_same_data_small(self):
        norm_data1 = [1, 5, 10]
        e = QQE(norm_data1, remove_outliers=True, estimate_quantile=False)
        me = e.predict_and_get_error(norm_data1, method="mean_err", remove_outliers=True)
        self.assertEqual(me, 0)

    def test_qq_same_data(self):
        norm_data1 = np.random.normal(size=200)
        e = QQE(norm_data1, remove_outliers=True, estimate_quantile=False)
        me = e.predict_and_get_error(norm_data1, method="mean_err", remove_outliers=True)
        self.assertLess(me, 0.1 ** 4)

    def test_qq_estimate_quantiles(self):
        d = [1, 5, 10]
        e = QQE(d, remove_outliers=False)
        estimated_base_eq = e._estimate_base_quantiles(d)
        self.assertListEqual([0.5/3, 1.5/3, 2.5/3], estimated_base_eq)

    def test_qq_exact_quantiles(self):
        d = [1, 5, 10]
        e = QQE(d, remove_outliers=False, estimate_quantile=False)
        estimated_base_eq = e._exact_base_quantiles(d)
        self.assertListEqual([0/2, 1/2.0, 1.0], estimated_base_eq)

    def test_qq_diff_dist1(self):
        norm_data1 = np.random.normal(size=200)
        data = np.random.beta(1, 2, size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_error(data, method="mean_err")
        # print("mean error: %f" % me)
        self.assertGreater(me, 0.1)

    def test_qq_diff_dist2(self):
        norm_data1 = np.random.normal(size=200)
        data = np.random.lognormal(size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_error(data, method="mean_err")
        # print("mean error: %f" % me)
        self.assertGreater(me, 0.1)

    def test_qq_diff_dist3(self):
        norm_data1 = np.random.normal(size=200)
        data = np.random.poisson(size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_error(data, method="mean_err")
        # print("mean error: %f" % me)
        self.assertGreater(me, 0.1)


if __name__ == '__main__':
    unittest.main()