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
job_log_dir="${this_dir}/job_logs" # dir to save logs of the failed jobs
mkdir -p "${job_log_dir}"

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

kill_job () (
    set +e
    # try to kill the LSF job
    local lsf_id="${1}"
    echo "[$(timestamp)] killing: ${lsf_id}"
    bkill ${lsf_id}
    local status=$?
    if [ "${status}" -ne "0" ]; then
        echo "[$(timestamp)] ERROR: bkill returned non-zero exit code, job ${lsf_id} may not have been killed"
    fi
)

lsf_job_logger() (
    set +e
    # try to log the metrics of the LSF job
    local lsf_id="${1}"
    local job_log_dir="${job_log_dir}"
    local job_log_txt="${job_log_dir}/${lsf_id}.txt"
    local job_log_json="${job_log_dir}/${lsf_id}.json"
    # check if job can be found
    bjobs ${lsf_id} 2>&1 | grep -q 'is not found'
    local status=$?
    # exit status of 0 if 'is not found'
    if [ "${status}" -ne "0" ]; then
        bjobs -l "${lsf_id}" > "${job_log_txt}"
        bjobs -o "jobid stat queue user user_group queue job_name job_description project application service_class job_group job_priority rsvid esub kill_reason dependency pend_reason command pids exit_code exit_reason from_host first_host exec_host nexec_host output_dir sub_cwd exec_home exec_cwd ask_hosts alloc_slot nalloc_slot host_file exclusive nreq_slot submit_time start_time estimated_start_time specified_start_time specified_terminate_time time_left finish_time estimated_run_time ru_utime ru_stime %complete warning_action action_warning_time pendstate pend_time ependtime ipendtime effective_plimit plimit_remain cpu_used run_time idle_factor exception_status slots mem max_mem avg_mem memlimit swap swaplimit gpu_num gpu_mode j_exclusive gpu_alloc nthreads hrusage min_req_proc max_req_proc network_req filelimit corelimit stacklimit processlimit runtimelimit plimit input_file output_file error_file output_dir sub_cwd exec_home exec_cwd energy gpfsio" -json "${lsf_id}" > "${job_log_json}"
    fi
)

# find all core dumps
find "${search_dir}/" -type f -regex "^.*core\.[0-9]*" | while read item; do
    # get the job id from core dump
    lsf_id="$(get_LSB_JOBID_from_core "${item}")"

    # check if we've already saved the job id
    if not_in_cache "${lsf_id}" ; then
        echo "[$(timestamp)] job not in cache: ${lsf_id}"
        # check if the job is still running
        if job_still_running ${lsf_id}; then
            echo "[$(timestamp)] job still running: ${lsf_id}"
            # do things here to stop job
            # kill_job "${lsf_id}"
        else
            # if the job is already dead, log its id so we can skip it next time
            echo "${lsf_id}" >> "$job_cache"
            lsf_job_logger "${lsf_id}"
        fi
    # else
    #     echo "[$(timestamp)] job in cache: ${lsf_id}"
    fi
done
