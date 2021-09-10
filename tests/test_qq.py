import unittest
import numpy as np
from qq.qqe import QQE


class QQTest(unittest.TestCase):

    def test_qq_same_dist(self):
        norm_data1 = np.random.normal(size=200)
        norm_data2 = np.random.normal(size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_mean_error(norm_data2)
        # print("mean error: %f" % me)
        self.assertLess(me, 0.1)

    def test_qq_diff_dist1(self):
        norm_data1 = np.random.normal(size=200)
        data = np.random.beta(1, 2, size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_mean_error(data)
        # print("mean error: %f" % me)
        self.assertGreater(me, 0.1)

    def test_qq_diff_dist2(self):
        norm_data1 = np.random.normal(size=200)
        data = np.random.lognormal(size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_mean_error(data)
        # print("mean error: %f" % me)
        self.assertGreater(me, 0.1)

    def test_qq_diff_dist3(self):
        norm_data1 = np.random.normal(size=200)
        data = np.random.poisson(size=200)
        e = QQE(norm_data1)
        me = e.predict_and_get_mean_error(data)
        # print("mean error: %f" % me)
        self.assertGreater(me, 0.1)


if __name__ == '__main__':
    unittest.main()