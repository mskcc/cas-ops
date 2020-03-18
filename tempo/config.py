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
PARENT_CONFIG = os.environ['PARENT_CONFIG'] # some extra inputs
# optional:
TIMESTAMP = os.environ.get('TIMESTAMP')
LOG_DIR = os.environ.get('LOG_DIR')
NXF_LOG = os.environ.get('NXF_LOG')
MAPPING_TSV = os.environ.get('MAPPING_TSV')
PAIRING_TSV = os.environ.get('PAIRING_TSV')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR')
LSB_JOBID = os.environ.get('LSB_JOBID')
LSB_OUTPUTFILE = os.environ.get('LSB_OUTPUTFILE')
CURDIR = os.environ.get('CURDIR', os.path.realpath('.'))

parent_config_data = json.load(open(PARENT_CONFIG))
project = parent_config_data.get('project')
pipeline = parent_config_data.get('pipeline')
version = parent_config_data.get('version')

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
'version': version
}


def main():
    """
    Main control function for the script
    """
    json.dump(config, open(CONFIG_JSON, "w"), indent = 4)

if __name__ == '__main__':
    main()
