#!/bin/bash
set -eu

# check for errors in the Tempo pipeline output

# Get locations for dirs and files from local dir and config.json
absdir="$(python -c 'import os; print(os.path.realpath("."))')"

configJSON="${absdir}/config.json"

lsf_log=$(
python - <<EOF
import os, json
print(json.load(open("${configJSON}"))['lsf_log'])
EOF
)

output_dir=$(
python - <<EOF
import os, json
print(json.load(open("${configJSON}"))['output_dir'])
EOF
)

nextflow_trace=$(
python - <<EOF
import os, json
print(json.load(open("${configJSON}"))['nextflow_trace'])
EOF
)

pipeline_exitcode=$(
python - <<EOF
import os, json
print(json.load(open("${configJSON}"))['pipeline_exitcode'])
EOF
)

work_dir="${absdir}/work"

set +e

# Functions for checking for errors
check_for_truncated_bams () {
    local search_dir="$1"
    val=$( { ( module load samtools/1.9; for i in $(find "${search_dir}" -type f -name "*.bam"); do samtools quickcheck $i 2>&1 ; done; ) ; } | wc -l )
    echo "${val}"
}

check_exit_code () {
    local exitcode_file="$1"
    local exitcode="$(head -1 "${exitcode_file}")"
    if [ ! "${exitcode}" -eq 0 ]; then echo "ERROR: pipeline exit code is ${exitcode}"; fi
}

task_breakdown () {
    local trace_file="$1"
    echo "Pipeline Task Breakdown:"
    tail -n +2 "${trace_file}" | cut -f7 | sort | uniq -c | sed -e 's|^ *||g'
    echo
}

number_retried_tasks () {
    local log_file="$1"
    local val="$(grep error "${log_file}" | grep 'Execution is retried' | wc -l)"
    echo "${val} Total Failed Tasks (retried)"
}

number_of_failed_retried_tasks () {
    local log_file="$1"
    local val="$(grep error "${log_file}" | grep 'Error is ignored' | wc -l)"
    echo "${val} Total Failed Tasks (ignored)"
}

echo ".bam files with potential errors in output dir:"
check_for_truncated_bams "${output_dir}"
echo

echo ".bam files with potential errors in work dir:"
check_for_truncated_bams "${work_dir}"
echo

task_breakdown "${nextflow_trace}"
number_retried_tasks "${lsf_log}"
number_of_failed_retried_tasks "${lsf_log}"
