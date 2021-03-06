import numpy as np
from ctapipe.io import zfits
from utils.mc_events_reader import hdf5_mc_event_source
import logging
import sys
import peakutils
from utils.logger import TqdmToLogger

from tqdm import tqdm


def run(hist, options, hist_type):
    """
    Fill the adcs Histogram out of darkrun/baseline runs
    :param h_type: type of Histogram to produce: ADC for all samples adcs or SPE for only peaks
    :param hist: the Histogram to fill
    :param options: see analyse_spe.py
    :param prev_fit_result: fit result of a previous step needed for the calculations
    :return:
    """
    log = logging.getLogger(sys.modules['__main__'].__name__+'.'+__name__)
    # Reading the file
    event_number = 0

    if not options.mc:
        log.info('Running on DigiCam data')
    else:
        log.info('Running on MC data')

    pbar = tqdm(total=options.max_event-options.min_event)

    for file in options.file_list:
        # Open the file
        _url = options.directory + options.file_basename % file

        if not options.mc:
            inputfile_reader = zfits.zfits_event_source(url=_url, max_events=options.max_event)  #TODO data_type arg does not exist anymore
        else:
            #inputfile_reader = ToyReader(filename=_url, id_list=[0],
            #                             max_events=options.max_event,
            #                             n_pixel=options.n_pixels, events_per_level=options.events_per_level)

            inputfile_reader = hdf5_mc_event_source(url=_url, events_per_dc_level=options.dc_step, events_per_ac_level=options.ac_step, dc_start=options.dc_start, ac_start=options.ac_start, max_events=options.max_event)


        log.debug('--|> Moving to file %s' % _url)
        # Loop over event in this file
        for event in inputfile_reader:

            if event_number > options.max_event:
                break

            if event_number < options.min_event:
                event_number += 1
                continue

            pbar.update(1)

            for telid in event.r0.tels_with_data:

                # Take data from zfits
                data = np.array(list(event.r0.tel[telid].adc_samples.values()))

                # Get rid off unwanted pixels


                data = data[options.pixel_list]


                if hist_type == 'raw':

                    hist.fill_with_batch(data)

                elif hist_type == 'integral':

                    temp = np.sum(data - 2000, axis=1) # TODO need to compress this <4095
                    hist.fill(temp)

                else:

                    log.info('Unknown hist_type = %s' %hist_type)

            event_number += 1

    return
