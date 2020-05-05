#!/bin/bash
set -euo pipefail

# This script will search for LSF core dump files and, if found, issue a kill command
# for their parent LSF jobs, if the jobs are still running
# Usage:
# $ ./lsf_coredump_killer.sh work

search_dir=$1
this_dir="$(readlink -f $(dirname $0))"
job_cache="${this_dir}/.job_coredump_cache" # file to store job id's that we've already checked
touch "${job_cache}"

timestamp () {
    date +"%Y-%m-%d %H:%M:%S"
}

get_LSB_JOBID_from_core () {
    # searches for the string that looks like 'LSB_JOBID=35745673' in the binary core dump
    local corefile="${1}"
    strings "${corefile}" | grep LSB_JOBID | cut -d '=' -f2
}

not_in_cache () (
    set +e # use subshell to modulate shellopt here
    # check if the given value is cached or not
    local search_value="${1}"
    local cache_file="${job_cache}"
    grep -q "${search_value}" "${cache_file}"
    local status="$?"
    if [ "${status}" == "1" ]; then
        true
    else
        false
    fi
)

job_still_running () (
    set +e
    # check if the LSF job is still running
    local lsf_id="${1}"
    local job_status="$(bjobs -noheader -o stat "${lsf_id}" 2>&1 )"
    if [ "${job_status}" == "RUN" ]; then
        true
    else
        false
    fi
)

# find all core dumps
find "${search_dir}/" -type f -regex "^.*core\.[0-9]*" | while read item; do
    # get the job id from core dump
    lsf_id="$(get_LSB_JOBID_from_core "${item}")"

    # check if we've already saved the job id
    if not_in_cache "${lsf_id}" ; then
        echo "[$(timestamp)] job not in cache: ${lsf_id}"
        if job_still_running ${lsf_id}; then
            echo "[$(timestamp)] job still running: ${lsf_id}"
            # do things here to stop job
        else
            # if the job is already dead, log its id so we can skip it next time
            echo "${lsf_id}" >> "$job_cache"
        fi
    # else
    #     echo "[$(timestamp)] job in cache: ${lsf_id}"
    fi
done
