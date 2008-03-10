#!/usr/bin/env python
#
#    License: GNU GPLv3
#
#    This file is part of Pylot.
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.  See the GNU General Public License 
#    for more details.
#


import sys
import time
import xmlparse
from threading import Thread
from pylot_engine import LoadManager



class ProgressBar:
    def __init__(self, duration, min_value = 0, max_value=100, total_width=40):
        self.prog_bar = '[]'  # This holds the progress bar string
        self.duration = duration
        self.min = min_value
        self.max = max_value
        self.span = max_value - min_value
        self.width = total_width
        self.amount = 0  # When amount == max, we are 100% done
        self.update_amount(0)  # Build progress bar string
    
    
    def update_amount(self, new_amount = 0):
        if new_amount < self.min: new_amount = self.min
        if new_amount > self.max: new_amount = self.max
        self.amount = new_amount
        
        # Figure out the new percent done, round to an integer
        diff_from_min = float(self.amount - self.min)
        percent_done = (diff_from_min / float(self.span)) * 100.0
        percent_done = round(percent_done)
        percent_done = int(percent_done)
        
        # Figure out how many hash bars the percentage should be
        all_full = self.width - 2
        num_hashes = (percent_done / 100.0) * all_full
        num_hashes = int(round(num_hashes))
        
        # build a progress bar with hashes and spaces
        self.prog_bar = '[' + '#' * num_hashes + ' ' * (all_full - num_hashes) + ']'
        
        # figure out where to put the percentage, roughly centered
        percent_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        percent_string = str(percent_done) + '%'

        # slice the percentage into the bar
        self.prog_bar = self.prog_bar[0:percent_place] + (percent_string + self.prog_bar[percent_place + len(percent_string):])
                    
    
    def update_time(self, new_time):
        self.update_amount((new_time / self.duration) * 100)

    
    def __str__(self):
        return str(self.prog_bar)



def start(num_agents, rampup, interval, duration, log_resps):
    runtime_stats = {}
    error_queue = []
    interval = interval / 1000.0  # convert from millisecs to secs
    
    # create a load manager
    lm = LoadManager(num_agents, interval, rampup, log_resps, runtime_stats, error_queue)
    
    # load the test cases
    try:
        cases = xmlparse.load_xml_cases()
        for req in cases:
            lm.add_req(req)
    except:  # if there was a problem getting cases from the xml file
        sys.stderr.write("Error opening testcase file.\n")
        sys.exit(1)
    
    start_time = time.time()
    
    # start the load manager
    lm.setDaemon(True)
    lm.start()
    
    pb = ProgressBar(duration)
    while (time.time() < start_time + duration):         
        time.sleep(.75)
        if lm.agents_started: 
            pb.update_time(time.time() - start_time)
            # ideally this will be refreshed on one line
            # still haven't figured out a platform independent way to do that
            print pb
    lm.stop()
    print 'generating results...'
    while lm.results_gen.isAlive():
        time.sleep(.05)
    print 'done.'
    