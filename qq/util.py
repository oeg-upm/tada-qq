
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
