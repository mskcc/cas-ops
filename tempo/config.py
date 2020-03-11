#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creates an updated config file for the pipeline
Save variables from the environment to JSON
Meant to be run from inside the Makefile, to propagate env vars to file for downstream usage
"""
import os
import json

CONFIG_JSON = os.environ['CONFIG_JSON'] # required
TIMESTAMP = os.environ.get('TIMESTAMP')
LOG_DIR = os.environ.get('LOG_DIR')
NXF_LOG = os.environ.get('NXF_LOG')
MAPPING_TSV = os.environ.get('MAPPING_TSV')
PAIRING_TSV = os.environ.get('PAIRING_TSV')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR')

config = {
"timestamp": TIMESTAMP,
"log_dir": LOG_DIR,
"nextflow_log": NXF_LOG,
"mapping_tsv": MAPPING_TSV,
"pairing_tsv": PAIRING_TSV,
"output_dir": OUTPUT_DIR
}


def main():
    """
    Main control function for the script
    """
    json.dump(config, open(CONFIG_JSON, "w"), indent = 4)

if __name__ == '__main__':
    main()
