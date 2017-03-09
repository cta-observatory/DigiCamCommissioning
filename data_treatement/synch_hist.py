import numpy as np
from ctapipe.io import zfits

import logging,sys
from tqdm import tqdm
from utils.logger import TqdmToLogger
from utils.toy_reader import ToyReader

def run(hist, options, min_evt = 5000.*3 , max_evt=5000*10):
    # Few counters
    evt_num, first_evt, first_evt_num = 0, True, 0

    log = logging.getLogger(sys.modules['__main__'].__name__+'.'+__name__)
    pbar = tqdm(total=max_evt-min_evt)
    tqdm_out = TqdmToLogger(log, level=logging.INFO)
    for file in options.file_list:

        if evt_num > max_evt: break
        # read the file
        _url = options.directory + options.file_basename % file

        inputfile_reader = None
        if not options.mc:
            inputfile_reader = zfits.zfits_event_source(url=_url, max_events=max_evt)

        else:
            inputfile_reader = ToyReader(filename=_url, id_list=[0], max_events=options.evt_max, n_pixel=options.n_pixels, events_per_level=options.evt_max/2, level_start=7)
        if options.verbose:
            log.debug('--|> Moving to file %s' % _url)
        # Loop over event in this file
        for event in inputfile_reader:
            if evt_num < min_evt:
                evt_num += 1
                continue
            else:
                # progress bar logging
                #if evt_num % int((max_evt-min_evt)/1000)==0: #TODO make this work properly
                pbar.update(1)
            if evt_num > max_evt: break
            for telid in event.dl0.tels_with_data:
                evt_num += 1
                if evt_num > max_evt: break
                # get the data
                data = np.array(list(event.dl0.tel[telid].adc_samples.values()))
                # subtract the pedestals
                data_max = np.argmax(data, axis=1)
                print(data_max[661])
                #if (data_max-np.argmin(data, axis=1))/data_max>0.2:
                hist.fill(data_max)

    # Update the errors
    # noinspection PyProtectedMember
    hist._compute_errors()
    # Save the histo in a file
    hist.save(options.output_directory + options.histo_filename) #TODO check for double saving
