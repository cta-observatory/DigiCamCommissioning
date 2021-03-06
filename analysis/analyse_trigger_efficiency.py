
#!/usr/bin/env python3

# external modules
import logging,sys
import numpy as np
from tqdm import tqdm
from utils.logger import TqdmToLogger


# internal modules
from data_treatement import trigger
from utils import display, histogram, geometry

__all__ = ["create_histo", "perform_analysis", "display_results", "save"]


def create_histo(options):
    """
    Create a list of ADC histograms and fill it with data
    :param options: a dictionary containing at least the following keys:
        - 'output_directory' : the directory in which the histogram will be saved (str)
        - 'histo_filename'   : the name of the file containing the histogram      (str)
        - 'synch_histo_filename'   : the name of the file containing the histogram      (str)
        - 'file_basename'    : the base name of the input files                   (str)
        - 'directory'        : the path of the directory containing input files   (str)
        - 'file_list'        : the list of base filename modifiers for the input files
                                                                                  (list(str))
        - 'evt_max'          : the maximal number of events to process            (int)
        - 'n_evt_per_batch'  : the number of event per fill batch. It can be
                               optimised to improve the speed vs. memory          (int)
        - 'n_pixels'         : the number of pixels to consider                   (int)
        - 'scan_level'       : number of unique poisson dataset                   (int)
        - 'adcs_min'         : the minimum adc value in histo                     (int)
        - 'adcs_max'         : the maximum adc value in histo                     (int)
        - 'adcs_binwidth'    : the bin width for the adcs histo                   (int)
    :return:
    """
    triggers = histogram.Histogram(data=np.zeros((len(options.scan_level), len(options.threshold))), \
                                 bin_centers=np.array(options.threshold), label='Trigger', \
                                 xlabel='Threshold [ADC]', ylabel='trigger rate [Hz]')



    #trigger_spectrum = trigger.run(triggers, options=options)
    trigger.run(triggers, options=options)
    triggers.save(options.output_directory + options.histo_filename)

    #np.save(arr=trigger_spectrum.ravel(), file=options.output_directory + options.trigger_spectrum_filename)

    return


def perform_analysis(options):
    """
    Perform a simple gaussian fit of the ADC histograms
    :param options: a dictionary containing at least the following keys:
        - 'output_directory' : the directory in which the histogram will be saved (str)
        - 'histo_filename'   : the name of the file containing the histogram
                                                 whose fit contains the gain,sigmas etc...(str)
    :return:
    """

    print('Nothing implemented')

    return


def display_results(options):
    """
    Display the analysis results
    :param options:
    :return:
    """

    # Load the histogram
    triggers = histogram.Histogram(filename=options.output_directory + options.histo_filename)


    import matplotlib.pyplot as plt


    plt.figure()
    plt.plot(triggers.bin_centers, triggers.data[0])
    plt.show()


#    fig = plt.figure()
#    axis = fig.add_subplot(111)
#    axis.hist(trigger_spectrum, bins=np.arange(int(np.min(trigger_spectrum)), int(np.max(trigger_spectrum))+1, 1), normed=True, label='spectrum cluster, 3 [MHz]')
#    plt.xlabel('Threshold [ADC]')
#    plt.legend(loc='best')
#    plt.ylabel('P')
#    axis.set_yscale('log')


    return


def save(options):

    print('Nothing implemented')

    return




