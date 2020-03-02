#!/bin/bash
# print selected LSF environment variables to console for logging
# do not print this one the % in the log path breaks things; LSB_JOBNAME
LSF_vars='LSB_BATCH_JID LSB_JOBID LSB_JOBFILENAME LSB_SUB_RES_REQ LSB_QUEUE LS_SUBCWD LSB_HOSTS LSB_DJOB_NUMPROC LSB_SUB_HOST LSB_OUTPUTFILE LSB_OUTDIR LSFUSER LS_JOBPID LSB_JOB_EXECUSER LSF_JOB_TIMESTAMP_VALUE LSB_BIND_CPU_LIST LSB_BIND_MEM_LIST LSB_JOBGROUP LSB_JOBINDEX LSB_JOBINDEX_STEP LSB_MAX_NUM_PROCESSORS'

for item in ${LSF_vars}; do printf "${item}: ${!item:-none}\n"; done;
