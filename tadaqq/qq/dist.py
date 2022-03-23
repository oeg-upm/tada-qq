import numpy as np


def get_stats(data):
    mean = np.mean(data)
    median = np.median(data)
    std = np.std(data)
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

