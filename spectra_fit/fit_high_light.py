import numpy as np
import utils.pdf

__all__ = ["p0_func", "slice_func", "bounds_func", "fit_func"]

#TODO Find p0, slice, bounds, from args=(y,x) if config==None


# noinspection PyUnusedLocal,PyUnusedLocal
def p0_func(y, x, *args, config=None, **kwargs):
    """
    find the parameters to start a mpe fit with low light
    :param y: the Histogram values
    :param x: the Histogram bins
    :param args: potential unused positionnal arguments
    :param config: should be the fit result of a previous fit
    :param kwargs: potential unused keyword arguments
    :return: starting points for []
    """

    if config==None:

        mu = mu_xt = gain = baseline = sigma_e = sigma_1 = amplitude = offset = np.nan
        param = [mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset]

    else:
        mu = 0.001
        mu_xt = 0.08 #config[1, 0]
        gain = config[1, 0]
        baseline = config[0, 0]
        sigma_e = config[2, 0]
        sigma_1 = config[3,0]
        amplitude = np.nan
        offset = 0.
        param = [mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset]


    #print(x)
    param[0] = np.average(x-param[3], weights=y) / param[2]
    #print(param[0])
    param[4] = np.sqrt(np.average((x - np.average(x, weights=y))**2, weights=y))/ param[2]
    param[5] = param[4]
    param[6] = np.sum(y)

    #print(param)

    return param


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def slice_func(y, x, *args, **kwargs):
    """
    returns the slice to take into account in the fit (essentially non 0 bins here)
    :param y: the Histogram values
    :param x: the Histogram bins
    :param args:
    :param kwargs:
    :return: the index to slice the Histogram
    """
    # Check that the Histogram has none empty values
    if np.where(x != 0)[0].shape[0] == 0:
        return [0, 1, 1]
    return [np.where(x != 0)[0][0], np.where(x != 0)[0][-1], 1]


# noinspection PyUnusedLocal,PyUnusedLocal
def bounds_func(*args, config=None, **kwargs):
    """
    return the boundaries for the parameters (essentially none for a gaussian)
    :param args:
    :param kwargs:
    :return:
    """

    param_min = [0., 0., 0., -np.inf, 0., 0., 0., -np.inf]
    param_max = [np.inf, 1, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]

    #print(param_min, param_max)

    return param_min, param_max


def fit_func(p, x,*args,**kwargs):
    """
    Simple gaussian pdf
    :param p: [norm,mean,sigma]
    :param x: x
    :return: G(x)
    """
    [mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset] = p
    return amplitude * utils.pdf.gaussian(x, sigma_e * gain ,  mu * (1+mu_xt) * gain + baseline)

def jac_func(x, *args, **kwargs):

    return #TODO compute jacobian matrix