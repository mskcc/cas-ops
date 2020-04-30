#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculate total execution time from all contiguous tasks in the timeline from Nextflow trace.txt
requires human readable times

$ ./calc_time.py trace.txt

NOTE: trace.txt might not contain the failed tasks from previous runs, causing differences in total time reported
"""
import sys
import csv
from datetime import datetime, timedelta
import argparse

def parse_timestamp(timestamp_str):
    """
    Convert a timestamp into a datetime object
    """
    return(datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f'))

def timedelta_to_string(timedelta, seconds = False):
    """
    Convert a timedelta object to string, optionally convert to seconds
    """
    if seconds == False:
        return(str(timedelta))
    if seconds == True:
        return(str(timedelta.total_seconds()))

def load_intervals(trace_file, sample_ids = None):
    """
    Loads all the intervals from a trace file
    Optionally, only outputs entries for samples that are included in the 'sample_ids' list

    Parameters
    ----------
    trace_file: str
        path to the Nextflow trace.txt file
    sample_ids: list|None
        a list of sample ID's to use for filtering output of intervals

    Output
    ------
    dict:
        a dictionary in the format of { status: set([ (submit, complete), ... ]), ... }, where 'submit' and 'complete' are datetime() objects
    """
    if sample_ids == None:
        sample_ids = []
    interval_sets = {}

    # load all the unqiue intervals from the trace file
    with open(trace_file) as fin:
        reader = csv.DictReader(fin, delimiter = '\t')
        for row in reader:
            status = row['status']

            # initialize the status if its not there already
            if status not in interval_sets:
                interval_sets[status] = set()

            # if sample_ids are passed, only add intervals that match the sample_id
            # if not sample_ids are passed, return all intervals
            if len(sample_ids) == 0:
                try:
                    # there might be some '-' values that raise an Exception ValueError
                    submit = parse_timestamp(row['submit'])
                    complete = parse_timestamp(row['complete'])
                    interval_sets[status].add((submit, complete))
                except ValueError:
                    pass
            else:
                # check that all sample_ids are in the tag
                tag = row['tag']
                if all([ sample_id in tag for sample_id in sample_ids ]):
                    try:
                        # there might be some '-' values that raise an Exception ValueError
                        submit = parse_timestamp(row['submit'])
                        complete = parse_timestamp(row['complete'])
                        interval_sets[status].add((submit, complete))
                    except ValueError:
                        pass

    return(interval_sets)

def calculate_interval_durations(intervals):
    """
    Calculates the duration for all contiguous time intervals

    Parameters
    ----------
    intervals: list
        a list of tuples/lists in the format of [ [ start, stop ], ... ], where 'start' and 'stop' are datetime() objects

    Output
    ------
    list
        a list of datetime.timedelta() objects
    """
    # sort all the intervals by  the first value
    sorted_intervals = sorted(list(intervals), key=lambda x: x[0])

    # find the overlapping intervals; https://www.geeksforgeeks.org/merging-intervals/
    merged_intervals = []
    start_date = datetime(1969, 12, 01, 23, 59, 59, 000000)  # a long time ago
    current_submit = start_date
    current_complete = start_date

    # collapse to find the longest contiguous time intervals between all overlapping intervals
    for i in range(len(sorted_intervals)):
        interval = sorted_intervals[i]
        submit = interval[0]
        complete = interval[1]
        if submit > current_complete:
            if i != 0:
                merged_intervals.append([current_submit, current_complete])
            current_complete = complete
            current_submit = submit
        else:
            if complete >= current_complete:
                current_complete = complete

        # if current_complete != start_date and [current_submit, current_complete] not in merged_intervals:
        #         merged_intervals.append([current_submit, current_complete])
        #  NOTE: Why is this included in the original algorithm?? It adds intervals to the list that shouldnt be there...

    # calucalute the duration of all remaining contiguous intervals
    durations = []
    for submit, complete in merged_intervals:
        duration = complete - submit
        durations.append(duration)
    return(durations)

def calculate_trace_duration(trace_file):
    """
    Calculate total execution time from all contiguous tasks in the timeline from Nextflow trace.txt
    requires human readable times

    Parameters
    ----------
    trace_file: str
        path to the Nextflow trace.txt file

    Output
    ------
    (total_durations, message)

    total_durations: datetime.timedelta
        the total duration of the pipeline tasks across all runs
    message: str
        pretty printed messages about the duration metrics
    """
    # get all the intervals per status
    interval_sets = load_intervals(trace_file)

    # get all the durations per status
    duration_sets = {}
    for status, intervals in interval_sets.items():
        durations = calculate_interval_durations(intervals)
        duration_sets[status] = durations

    # get the total duration per status
    total_durations = {}
    for status, durations in duration_sets.items():
        total_duration = sum(durations, timedelta())
        total_durations[status] = total_duration

    # create a message to use for printing
    # list the time for each status type, then the total time
    message = ""
    for status, total_duration in total_durations.items():
        message += """{status}: {total_duration} ({num_intervals} intervals)
""".format(status = status, total_duration = total_duration, num_intervals = len(interval_sets[status]))
    message += "Total: {total_duration} ({num_intervals} intervals)".format(
    total_duration = sum([ total_duration for status, total_duration in total_durations.items() ], timedelta()),
    num_intervals = len([ interval for status, intervals in interval_sets.items() for interval in intervals ])
    )

    return(total_durations, message)

def load_samples(mapping_file):
    """
    Load all the sample IDs from the Tempo mapping file
    """
    samples = set()
    with open(mapping_file) as fin:
        reader = csv.DictReader(fin, delimiter = '\t')
        for row in reader:
            sample = row['SAMPLE']
            samples.add(sample)
    return(list(samples))

def calc_time_trace(**kwargs):
    """
    Prints out the contiguous time intervals from a trace file

    $ ./calc_time.py trace logs/2020-04-21_12-43-46/trace.txt
    CACHED: 4 days, 18:46:27.316000 (4585 intervals)
    FAILED: 0:00:00 (7 intervals)
    COMPLETED: 9:10:32.294000 (20 intervals)
    Total: 5 days, 3:56:59.610000 (4612 intervals)
    """
    trace_file = kwargs.pop('trace_file')
    total_durations, message = calculate_trace_duration(trace_file)
    print(message)

def calc_time_samples_durations(trace_file, mapping_file, seconds = False):
    """
    Calculate the contiguous time intervals for all samples in the trace file
    """
    # get the sample_ids from the mapping file
    samples = load_samples(mapping_file)

    # initialize dict to hold the per-sample intervals per status
    # { sample_id: {'CACHED': set([...]), ... }, ...  }
    sample_interval_sets = {}
    for sample in samples:
        # this is very inefficient since we are parsing the entire trace file repeatedly;
        # TODO: come up with a way to optimize this
        interval_sets = load_intervals(trace_file = trace_file, sample_ids = [sample])
        sample_interval_sets[sample] = interval_sets

    # calculate the duration for each sample
    sample_duration_sets = {}
    for sample, interval_sets in sample_interval_sets.items():
        for status, intervals in interval_sets.items():
            if sample not in sample_duration_sets:
                sample_duration_sets[sample] = {}
            durations = calculate_interval_durations(intervals)
            sample_duration_sets[sample][status] = durations

    # get the total duration per sample per status
    # total_sample_durations = {}
    total_sample_status_durations = {}
    for sample, duration_sets in sample_duration_sets.items():
        for status, durations in duration_sets.items():
            if sample not in total_sample_status_durations:
                total_sample_status_durations[sample] = {}
            total_duration = sum(durations, timedelta())
            total_sample_status_durations[sample][status] = total_duration

    # get the total duration per sample
    total_sample_durations = []
    for sample, duration_sets in total_sample_status_durations.items():
        total_sample_duration = timedelta()
        for status, total_duration in duration_sets.items():
            total_sample_duration += total_duration
        total_sample_durations.append((sample, total_sample_duration))

    # sort all the durations by length of time
    total_sample_durations = sorted(total_sample_durations, reverse= True, key=lambda x: x[1])

    # generate a pretty printed message about the results
    message = ""
    for sample, total_duration in total_sample_durations:
        message += "{sample}: {total_duration}\n".format(
            sample = sample,
            total_duration = timedelta_to_string(total_duration, seconds = seconds)
            )
    return(total_sample_durations, message)

def calc_time_samples(**kwargs):
    """
    Print out the total duration per sample to console

    $ ./calc_time.py samples logs/2020-04-21_12-43-46/trace.txt --seconds
    """
    trace_file = kwargs.pop('trace_file')
    mapping_file = kwargs.pop('mapping_file')
    seconds = kwargs.pop('seconds')
    total_sample_durations, message = calc_time_samples_durations(trace_file, mapping_file, seconds)
    print(message)

def main():
    """
    Main control function for the script when run from CLI
    """
    parser = argparse.ArgumentParser(description = 'Calculate the total duration of contiguous time intervals from Nextflow trace file')
    subparsers = parser.add_subparsers(help ='Sub-commands available')

    # subparser for trace.txt calculation
    trace_file = subparsers.add_parser('trace', help = 'Calculate duration of all intervals in a trace.txt file')
    trace_file.add_argument('trace_file', help = 'The Nextflow trace file to calculate')
    trace_file.set_defaults(func = calc_time_trace)

    # subparser for per-sample time durations
    trace_samples = subparsers.add_parser('samples', help = 'Calculate duration of all intervals in a trace.txt file')
    trace_samples.add_argument('trace_file', help = 'The Nextflow trace file to calculate')
    trace_samples.add_argument('mapping_file', nargs='?', default="mapping.tsv", help = 'The Tempo mapping file to read sample IDs from')
    trace_samples.add_argument('--seconds', action = "store_true", help = 'Whether to report output in seconds or not')
    trace_samples.set_defaults(func = calc_time_samples)

    args = parser.parse_args()
    args.func(**vars(args))

if __name__ == '__main__':
    main()
