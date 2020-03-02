#!/bin/bash
# top-level environment needed to run Tempo Nextflow on Juno HPC
set -e
module unload java && module load java/jdk1.8.0_202
module unload singularity && module load singularity/3.1.1
