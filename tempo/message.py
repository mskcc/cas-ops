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

# load the JSON and get some values
CONFIG_JSON = os.environ['CONFIG_JSON'] # required; get from Makefile enviornment
# CURDIR = os.environ.get('CURDIR', os.path.realpath('.'))
config = json.load(open(CONFIG_JSON))
nextflow_log = config['nextflow_log']
log_dir = config['log_dir']
pipeline_dir = config['pipeline_dir']
lsf_log = config['lsf_log']
lsf_jobid = config['lsf_jobid']

# pre-build some common message snippets to be used later
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

# functions to return message body text
def started():
    message = """Pipeline started in directory:
{pipeline_dir}

{lsf_jobid_message}

{log_dir_message}

{lsf_log_message}

{nextflow_log_message}
""".format(
    pipeline_dir = pipeline_dir,
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
""".format(
    pipeline_dir = pipeline_dir,
    log_dir_message = log_dir_message,
    lsf_log_message = lsf_log_message,
    nextflow_log_message = nextflow_log_message
    )
    return(message)

def failed():
    message = """Pipeline failed in directory:
{pipeline_dir}

{log_dir_message}

{lsf_log_message}

{nextflow_log_message}
""".format(
    pipeline_dir = pipeline_dir,
    log_dir_message = log_dir_message,
    lsf_log_message = lsf_log_message,
    nextflow_log_message = nextflow_log_message
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

    data = make_body(message_func)
    print(json.dumps(data, indent = 4))
