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

def load_intervals(trace_file):
    """
    """
    interval_sets = {}
    # intervals = set()

    # load all the unqiue intervals from the trace file
    with open(trace_file) as fin:
        reader = csv.DictReader(fin, delimiter = '\t')
        for row in reader:
            try:
                status = row['status']
                if status not in interval_sets:
                    interval_sets[status] = set()
                # there might be some '-' values
                submit = datetime.strptime(row['submit'], '%Y-%m-%d %H:%M:%S.%f')
                complete = datetime.strptime(row['complete'], '%Y-%m-%d %H:%M:%S.%f')
                interval_sets[status].add((submit, complete))
            except:
                pass
    return(interval_sets)

def calculate_interval_durations(intervals):
    """
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
    message = ""
    for status, total_duration in total_durations.items():
        message += """{status}: {total_duration} ({num_intervals} intervals)
""".format(status = status, total_duration = total_duration, num_intervals = len(interval_sets[status]))
    message += "Total: {total_duration} ({num_intervals} intervals)".format(
    total_duration = sum([ total_duration for status, total_duration in total_durations.items() ], timedelta()),
    num_intervals = len([ interval for status, intervals in interval_sets.items() for interval in intervals ])
    )

    return(total_durations, message)

def main():
    """
    Main control function for the script when run from CLI
    """
    args = sys.argv[1:]
    trace_file = args[0]
    total_durations, message = calculate_trace_duration(trace_file)
    print(message)

if __name__ == '__main__':
    main()
