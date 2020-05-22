#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates an updated config file for the pipeline
Save variables from the environment to JSON for downstream usage
Meant to be run from inside the Makefile, optionally from inside LSF job from command
make submit
"""
import os
import json

# get environment variables
# required:
CONFIG_JSON = os.environ['CONFIG_JSON'] # output file

# optional:
TIMESTAMP = os.environ.get('TIMESTAMP')
LOG_DIR = os.environ.get('LOG_DIR')
NXF_LOG = os.environ.get('NXF_LOG')
NXF_TRACE = os.environ.get('NXF_TRACE')
MAPPING_TSV = os.environ.get('MAPPING_TSV')
PAIRING_TSV = os.environ.get('PAIRING_TSV')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR')
LSB_JOBID = os.environ.get('LSB_JOBID')
LSB_OUTPUTFILE = os.environ.get('LSB_OUTPUTFILE')
CURDIR = os.environ.get('CURDIR', os.path.realpath('.'))
PIPELINE_EXITCODE_FILE = os.environ.get('PIPELINE_EXITCODE_FILE')
PROJECT_FILE = os.environ.get('PROJECT_FILE', "../.project") # .project file in parent dir
TEMPO_VERSION_FILE = os.environ.get('TEMPO_VERSION_FILE', ".version") # .version

with open(PROJECT_FILE) as fin:
    project = fin.readlines()[0].strip()
with open(TEMPO_VERSION_FILE) as fin:
    version = fin.readlines()[0].strip()
pipeline = "tempo"


config = {
"timestamp": TIMESTAMP,
"log_dir": LOG_DIR,
"nextflow_log": NXF_LOG,
"mapping_tsv": MAPPING_TSV,
"pairing_tsv": PAIRING_TSV,
"output_dir": OUTPUT_DIR,
"lsf_jobid": LSB_JOBID,
"lsf_log": LSB_OUTPUTFILE,
"pipeline_dir": CURDIR,
'pipeline': pipeline,
'project': project,
'version': version,
'nextflow_trace': NXF_TRACE,
'pipeline_exitcode': PIPELINE_EXITCODE_FILE
}


def main():
    """
    Main control function for the script
    """
    json.dump(config, open(CONFIG_JSON, "w"), indent = 4)

if __name__ == '__main__':
    main()
