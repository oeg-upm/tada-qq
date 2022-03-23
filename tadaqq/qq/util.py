import math


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


def errors_mean(y_pred, y_real):
    """
    :param y_pred: list of predicted
    :param y_real: list of real
    :return:
    """
    if len(y_pred) != len(y_real):
        print("Error, unmatched number of ys")
        return None
    tot_err = 0.0
    for i in range(len(y_pred)):
        tot_err += abs(y_pred[i]-y_real[i])
    mean_tot_err = tot_err/len(y_pred)
    # print("total error: "+str(tot_err))
    # print("mean error: "+str(mean_tot_err))
    return mean_tot_err


def errors_sq_mean(y_pred, y_real):
    """
    :param y_pred: list of predicted
    :param y_real: list of real
    :return:
    """
    if len(y_pred) != len(y_real):
        print("Error, unmatched number of ys")
        return None
    tot_err = 0.0
    for i in range(len(y_pred)):
        tot_err += (y_pred[i]-y_real[i]) ** 2
    mean_tot_err = tot_err/len(y_pred)
    return mean_tot_err


def errors_sq1_mean(y_pred, y_real):
    """
    like sq_mean but with one always added ot the err difference so the square of the error won't
    get smaller if the difference is less than 1
    :param y_pred: list of predicted
    :param y_real: list of real
    :return:
    """
    if len(y_pred) != len(y_real):
        print("Error, unmatched number of ys")
        return None
    tot_err = 0.0
    for i in range(len(y_pred)):
        tot_err += (abs(y_pred[i]-y_real[i]) + 1) ** 2
    mean_tot_err = tot_err/len(y_pred)
    # print("total error: "+str(tot_err))
    # print("mean error: "+str(mean_tot_err))
    return mean_tot_err


def errors_sqroot_mean(y_pred, y_real):
    """
        :param y_pred: list of predicted
    :param y_real: list of real
    """
    if len(y_pred) != len(y_real):
        print("Error, unmatched number of ys")
        return None
    tot_err = 0.0
    for i in range(len(y_pred)):
        tot_err += math.sqrt(abs(y_pred[i]-y_real[i]))
    mean_tot_err = tot_err/len(y_pred)
    return mean_tot_err