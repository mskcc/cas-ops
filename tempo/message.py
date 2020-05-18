#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create success and failure messages for the pipeline
By reading from values saved in the config.json
Meant to be run from inside the Makefile
"""
import os
import sys
import json
import calc_time

# load the JSON and get some values
CONFIG_JSON = os.environ['CONFIG_JSON'] # required; get from Makefile enviornment
ERROR_MESSAGE = os.environ.get('ERROR_MESSAGE') # text file that can hold more custom post-pipeline error checking messages
# CURDIR = os.environ.get('CURDIR', os.path.realpath('.'))
config = json.load(open(CONFIG_JSON))
nextflow_log = config.get('nextflow_log')
log_dir = config.get('log_dir')
pipeline_dir = config.get('pipeline_dir')
lsf_log = config.get('lsf_log')
lsf_jobid = config.get('lsf_jobid')
project = config.get('project')
pipeline = config.get('pipeline')
version = config.get('version')
nextflow_trace = config.get('nextflow_trace')
mapping_tsv = config.get('mapping_tsv', "mapping.tsv")

# pre-build some common message snippets to be used later
project_pipeline_version_message = """
Project: {project}
Pipeline: {pipeline}
Version: {version}
""".format(
project = project,
pipeline = pipeline,
version = version
)


lsf_jobid_message = """
LSF job id: {lsf_jobid}
""".format(lsf_jobid = lsf_jobid)

log_dir_message = """
log dir:
{log_dir}
""".format(log_dir = log_dir)

nextflow_log_message = """
Nextflow log:
{nextflow_log}
""".format(nextflow_log = nextflow_log)

lsf_log_message = """
LSF log:
{lsf_log}
""".format(lsf_log = lsf_log)

error_message = ""
if ERROR_MESSAGE and os.path.exists(ERROR_MESSAGE):
    error_message = open(ERROR_MESSAGE).read()

# if the nextflow_trace file exists, then calculate the total execution time for it
duration_message = ""
samples_duration_messages = ""
if os.path.exists(nextflow_trace):
    total_durations, duration_message = calc_time.calculate_trace_duration(nextflow_trace)
    duration_message = """
Total Accumulated Pipeline Execution Time:
{duration_message}
""".format(duration_message = duration_message)
    project_pipeline_version_message += duration_message

    # if the mapping tsv exists, then get the samples message as well
    if os.path.exists(mapping_tsv):
        total_sample_durations, samples_duration_messages = calc_time.calc_time_samples_durations(
            trace_file = nextflow_trace, mapping_file = mapping_tsv)
        samples_duration_messages = """
Sample Execution Time Breakdown:
{samples_duration_messages}
""".format(samples_duration_messages = samples_duration_messages)



# functions to return message body text
def started():
    message = """Pipeline started in directory:
{pipeline_dir}

{project_pipeline_version_message}
{lsf_jobid_message}

{log_dir_message}

{lsf_log_message}

{nextflow_log_message}
""".format(
    pipeline_dir = pipeline_dir,
    project_pipeline_version_message = project_pipeline_version_message,
    lsf_jobid_message = lsf_jobid_message,
    log_dir_message = log_dir_message,
    lsf_log_message = lsf_log_message,
    nextflow_log_message = nextflow_log_message
    )
    return(message)

def success():
    message = """Pipeline finished successfully in directory:
{pipeline_dir}

{log_dir_message}

{lsf_log_message}

{nextflow_log_message}

{error_message}

{duration_message}

{samples_duration_messages}
""".format(
    pipeline_dir = pipeline_dir,
    log_dir_message = log_dir_message,
    lsf_log_message = lsf_log_message,
    nextflow_log_message = nextflow_log_message,
    error_message = error_message,
    duration_message = duration_message,
    samples_duration_messages = samples_duration_messages
    )
    return(message)

def failed():
    message = """Pipeline failed in directory:
{pipeline_dir}

{log_dir_message}

{lsf_log_message}

{nextflow_log_message}

{error_message}

{duration_message}
""".format(
    pipeline_dir = pipeline_dir,
    log_dir_message = log_dir_message,
    lsf_log_message = lsf_log_message,
    nextflow_log_message = nextflow_log_message,
    error_message = error_message,
    duration_message = duration_message,
    samples_duration_messages = samples_duration_messages
    )
    return(message)

def killed():
    message = """Pipeline leader job killed in directory:
{pipeline_dir}

{log_dir_message}

{lsf_log_message}

{nextflow_log_message}

{error_message}

{duration_message}
""".format(
    pipeline_dir = pipeline_dir,
    log_dir_message = log_dir_message,
    lsf_log_message = lsf_log_message,
    nextflow_log_message = nextflow_log_message,
    error_message = error_message,
    duration_message = duration_message,
    samples_duration_messages = samples_duration_messages
    )
    return(message)

def make_body(func):
    data = {}
    data['body'] = func()
    return(data)

if __name__ == '__main__':
    args = sys.argv[1:]
    message_type = args[0]
    if message_type == "success":
        message_func = success
    if message_type == "failed":
        message_func = failed
    if message_type == "started":
        message_func = started
    if message_type == "killed":
        message_func = killed

    data = make_body(message_func)
    print(json.dumps(data, indent = 4))
