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

CONFIG_JSON = os.environ['CONFIG_JSON'] # required; get from Makefile enviornment
CURDIR = os.environ.get('CURDIR', os.path.realpath('.'))
config = json.load(open(CONFIG_JSON))
nextflow_log = config['nextflow_log']
log_dir = config['log_dir']

def started():
    message = """Pipeline started in directory:
{CURDIR}

log dir:
{log_dir}

Nextflow log:
{nextflow_log}
""".format(
    CURDIR = CURDIR,
    log_dir = log_dir,
    nextflow_log = nextflow_log
    )
    return(message)

def success():
    message = """Pipeline finished successfully in directory:
{CURDIR}

log dir:
{log_dir}

Nextflow log:
{nextflow_log}
""".format(
    CURDIR = CURDIR,
    log_dir = log_dir,
    nextflow_log = nextflow_log
    )
    return(message)

def failed():
    message = """Pipeline failed in directory:
{CURDIR}

log dir:
{log_dir}

Nextflow log:
{nextflow_log}
""".format(
    CURDIR = CURDIR,
    log_dir = log_dir,
    nextflow_log = nextflow_log
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
