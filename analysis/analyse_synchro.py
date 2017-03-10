#!/usr/bin/env python3

# external modules

# internal modules
from data_treatement import synch_hist
from utils import display, histogram, geometry
import logging,sys
import numpy as np

__all__ = ["create_histo", "perform_analysis", "display_results"]


def create_histo(options):
    """
    Create a list of ADC histograms and fill it with data

    :param options: a dictionary containing at least the following keys:
        - 'output_directory' : the directory in which the histogram will be saved (str)
        - 'histo_filename'   : the name of the file containing the histogram      (str)
        - 'file_basename'    : the base name of the input files                   (str)
        - 'directory'        : the path of the directory containing input files   (str)
        - 'file_list'        : the list of base filename modifiers for the input files
                                                                                  (list(str))
        - 'evt_min'          : the minimal event number to process                (int)
        - 'evt_max'          : the maximal event number to process                (int)
        - 'n_pixels'         : the number of pixels to consider                   (int)
        - 'sample_max'       : the maximum number of sample                       (int)

    :return:
    """
    # Define the histograms
    peaks = histogram.Histogram(bin_center_min=1, bin_center_max=options.adcs_max,
                               bin_width=1, data_shape=(len(options.scan_level),len(options.pixel_list),),
                               label='Position of the peak',xlabel='Sample [/ 4 ns]',ylabel = 'Events / sample')

    # Get the adcs
    synch_hist.run(peaks, options)

    # Save the histogram

    peaks.save(options.output_directory + options.histo_filename)


    print(peaks.data.shape)
    # Delete the histograms
    del peaks


    return


def perform_analysis(options):
    """
    Perform a simple gaussian fit of the ADC histograms

    :param options: a dictionary containing at least the following keys:
        - 'output_directory' : the directory in which the histogram will be saved (str)
        - 'histo_filename'   : the name of the file containing the histogram      (str)
        - 'hv_off_histo_filename' : the name of the hv_off fit results            (str)

    :return:
    """
    # Fit the baseline and sigma_e of all pixels
    log = logging.getLogger(sys.modules['__main__'].__name__+__name__)

    log.info('No analysis is implemented for peaks determination')


def display_results(options):
    """
    Display the analysis results

    :param options:

    :return:
    """

    # Load the histogram
    peaks = histogram.Histogram(filename=options.output_directory + options.histo_filename)

    # Define Geometry
    geom = geometry.generate_geometry_0(options.n_pixels)

    # Perform some plots

    display.display_hist(peaks,  geom)

    input('press button to quit')

    return
