import numpy as np
from scipy.optimize import curve_fit
import peakutils
import logging,sys
import utils.pdf

__all__ = ["p0_func", "slice_func", "bounds_func", "fit_func"]


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
    log = logging.getLogger(sys.modules['__main__'].__name__ + '.' + __name__)
    if config is not None:

        ## Load from previous result

        baseline = 0.
        if np.where(y != 0)[0].shape[0] > 2:
            baseline = x[np.where(y != 0)[0][0]] + 4.*4 # baseline
            if baseline>config[0, 0]:
                baseline = config[0, 0]-config[1, 0]/2
        #baseline = config[0, 0]

        gain = config[1, 0]
        sigma_e = config[2, 0]
        sigma_1 = config[3, 0]

        ## Compute estimate

        amplitude = np.sum(y)
        mean = (np.average(x,weights=y)-baseline)/gain
        #start = y.flat[np.abs(x - (baseline - gain/2.)).argmin()]
        #end = y.flat[np.abs(x - (baseline + gain/2.)).argmin()]
        #print(baseline,gain,start,end,np.sum(y[start:end]),amplitude)
        mu = max(0,mean) #- np.log(float(np.sum(y[start:end]))/amplitude)
        mu_xt = 0.
        offset = 0.

        param = [mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset]
        #print(param)
        return param

    else :

        amplitude = np.sum(y)
        offset = 0.
        threshold = 0.3
        min_dist = 3.

        peak_index = peakutils.indexes(y, threshold, min_dist)
        photo_peak = np.arange(0, len(peak_index), 1)


        if len(peak_index)<=2:

            gain = np.max(x[y>0]) - np.min(x[y>0])
            baseline = np.min(x[y>0]) + gain/2.
            start = int(baseline - gain / 2.)
            end = int(baseline + gain / 2.)

        else:

            gain = np.mean(np.diff(x[peak_index]))
            baseline = np.min(x[y>0]) + gain/2.
            start = int(baseline - gain / 2.)
            end = int(baseline + gain / 2.)

        mu = - np.log(np.sum(y[start:end]/amplitude))
        mu_xt = 0.06


        sigma = np.zeros(peak_index.shape[-1])

        for i in range(sigma.shape[-1]):

            start = max(int(peak_index[i] - gain/2.), 0)
            end = min(int(peak_index[i] + gain/2.), len(x))

            try:

                temp = np.average(x[start:end], weights=y[start:end])
                sigma[i] = np.sqrt(np.average((x[start:end] - temp) ** 2, weights=y[start:end]))

            except Exception as inst:
                log.error('Could not compute weights for sigma !!!')
                sigma[i] = gain/2.

        sigma_n = lambda sigma_e, sigma_1, n: np.sqrt(sigma_e ** 2 + n * sigma_1 ** 2)
        sigmas, sigma_error = curve_fit(sigma_n, photo_peak, sigma, bounds=[0., np.inf])

        sigma_e = sigmas[0]
        sigma_1 = sigmas[1]

        param = [mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset]

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
    #if np.where(y != 0)[0].shape[0] == 0:
    #    return []
    #max_bin = np.where(y != 0)[0][0]
    #if x[max_bin]== 4095: max_bin-=1
    return [np.where(y != 0)[0][0], np.where(y != 0)[0][-1], 1]


# noinspection PyUnusedLocal,PyUnusedLocal
def bounds_func(y,x,*args, config=None, **kwargs):
    """
    return the boundaries for the parameters (essentially none for a gaussian)
    :param args:
    :param kwargs:
    :return:
    """

    if config is None:

        param_min = [0., 0., 0., 0., 0., 0., 0., 0.]
        param_max = [200., 1., np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]

        return param_min, param_max

    else:
        '''
        mu = config[0]
        mu_xt = config[1]
        gain = config[2]
        baseline = config[3]
        sigma_e = config[4]
        sigma_1 = config[5]
        amplitude = config[6]
        offset = config[7] # TODO remove this guy
        '''
        baseline = config[0]
        gain = config[1]
        sigma_e = config[2]
        sigma_1 = config[3]
        param_min = [0.    , 0., gain[0] - 5*gain[1]    , baseline[0]-2*gain[0], sigma_e[0] /2 , sigma_1[0] /2 ,0.,-np.inf]
        param_max = [np.inf, 1. , gain[0] + 5*gain[1], baseline[0]+3., sigma_e[0] *2, sigma_1[0] *2,np.inf, np.inf]


        #if np.where(y != 0)[0].shape[0] > 2:
        #    if x[np.where(y != 0)[0][0]] + 4.*4  < baseline[0]:
        #        param_min[3]  = x[np.where(y != 0)[0][0]] + 4  # baseline
    #print(param_min)
    #print(param_max)
    return param_min, param_max


def fit_func(p, x, *args, **kwargs):
    """
    Simple gaussian pdf
    :param p: [norm,mean,sigma]
    :param x: x
    :return: G(x)
    """
    #mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset, variance = p
    mu, mu_xt, gain, baseline, sigma_e, sigma_1, amplitude, offset = p
    temp = np.zeros(x.shape)
    n_peak=40
    n_peakmin = 0
    # TODO avoir si ca marche quand on utilise en high light
    if len(x)>0:
        n_peak = int(float(x[-1] - baseline) / gain * 1.5)
        n_peakmin = max(0,int(float(x[0] - baseline) / gain * 0.7))

    x = x - baseline
    for n in range(n_peakmin,n_peak):
        sigma_n = np.sqrt(sigma_e ** 2 + n * sigma_1 ** 2 + 1./12.) # * gain
        param_gauss = [sigma_n, n*gain, 1.]
        temp += utils.pdf.generalized_poisson(n, mu, mu_xt) * utils.pdf.gaussian(param_gauss, x)

    return temp * amplitude

def label_func(*args, ** kwargs):
    """
    List of labels for the parameters
    :return:
    """
    label = ['$\mu$ [p.e.]', '$\mu_{XT}$ [p.e.]', 'Gain [LSB/p.e.]','Baseline [LSB]','$\sigma_e$ [LSB]', '$\sigma_1$ [LSB]', 'Amplitude', 'Offset [LSB]']
    return np.array(label)

if __name__ == '__main__':

    print('Nothing implemented')