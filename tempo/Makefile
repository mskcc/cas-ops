define help
This is the Makefile for CAS-OPS Tempo analysis

This directory should have been 'deployed' from a copy of the Makefile in the parent directory.

Create a Jira ticket with:

make jira-create

Then submit the pipeline with:

make submit

The default submission recipe will update the Jira ticket on pipeline start and finish

endef
export help
help:
	@printf "$$help"
.PHONY : help

SHELL:=/bin/bash
UNAME:=$(shell uname)
HOSTNAME:=$(shell hostname)
export TIMESTAMP:=$(shell date +"%Y-%m-%d_%H-%M-%S")
EMAIL_USER:=$(shell whoami)
EMAIL_HOST:=mskcc.org
EMAIL_ADDRESS:=$(EMAIL_USER)@$(EMAIL_HOST)
export PROJECT_FILE:=../.project
CONFIG_TEMPLATE:=.config.json
export CONFIG_JSON:=config.json
export LOG_DIR:=$(CURDIR)/logs/$(TIMESTAMP)
# export NXF_ANSI_LOG:=false
export NXF_ANSI_LOG:=true
export NXF_VER:=20.01.0
export NXF_WORK:=$(CURDIR)/work
export NXF_PID_FILE:=$(CURDIR)/.nextflow.pid
export NXF_REPORT:=$(LOG_DIR)/nextflow.html
export NXF_TIMELINE:=$(LOG_DIR)/timeline.html
export NXF_TRACE:=$(LOG_DIR)/trace.txt
export NXF_LOG:=$(LOG_DIR)/nextflow.log
export STDOUT_LOG:=$(LOG_DIR)/nextflow.stdout.log
export PATH:=$(CURDIR):$(PATH)
export ENV:=env.juno.sh

# ~~~~~ INSTALL & SETUP ~~~~~ #
# install Nextflow executable in current directory
./nextflow:
	@source "$(ENV)"; \
	curl -fsSL get.nextflow.io | bash

# settings for Tempo
# https://ccstempo.netlify.com/juno-setup.html#temporary-files
export TMPDIR=/scratch/$(shell whoami)
export NXF_SINGULARITY_CACHEDIR=/juno/work/taylorlab/cmopipeline/singularity_images
export TEMPO_VERSION_FILE:=$(CURDIR)/.version
export TEMPO_VERSION:=$(shell head -1 $(TEMPO_VERSION_FILE))
tempo/.git:
	git clone git@github.com:mskcc/tempo.git
tempo: tempo/.git
	@cd tempo && git checkout "$(TEMPO_VERSION)"
.PHONY: tempo

# creates the log directory for the execution instance; this should be called
# as a requirement for all recipes that write to log dir
$(LOG_DIR):
	@mkdir -p "$(LOG_DIR)"

# initialize the local dir for pipeline execution
init: ./nextflow tempo

# create a local config file to record environment variables such as timestamp and log dirs
config:
	python config.py

# ~~~~~ RUN ~~~~~ #
export MAPPING_TSV:=$(CURDIR)/mapping.tsv
export PAIRING_TSV:=$(CURDIR)/pairing.tsv
export OUTPUT_DIR:=$(CURDIR)/output

# extra configs for CAS Tempo usage
export TEMPO_CONFIG:=$(CURDIR)/tempo-1.3.config

# run in the current process
run: init $(MAPPING_TSV) $(PAIRING_TSV) $(LOG_DIR)
	[ ! -f "$(MAPPING_TSV)" ] && echo ">>> ERROR: mapping file does not exist; $(MAPPING_TSV)" && exit 1 || :
	[ ! -f "$(PAIRING_TSV)" ] && echo ">>> ERROR: pairing file does not exist; $(PAIRING_TSV)" && exit 1 || :
	source "$(ENV)" ; \
	nextflow \
	-log "$(NXF_LOG)" \
	-c "$(TEMPO_CONFIG)" \
	run tempo/pipeline.nf \
	-resume \
	-profile juno \
	--aggregate \
	--QC \
	--genome 'GRCh37' \
	--somatic \
	--mapping "$(MAPPING_TSV)" \
	--pairing "$(PAIRING_TSV)" \
	--outDir "$(OUTPUT_DIR)" \
	-with-report "$(NXF_REPORT)" \
	-with-timeline "$(NXF_TIMELINE)" \
	-with-trace "$(NXF_TRACE)" \
	-process.clusterOptions='-sla CMOPI'
	# | \
	# tee -a "$(STDOUT_LOG)"

# run in the background; capture Nextflow process ID and save to file
# use this for running inside an LSF job where you need to pass
# KILL signal to Nextflow for clean shutdown
# make sure set -e is not set because that causes exit after 'wait' on failed pipeline
export PIPELINE_EXITCODE_FILE:=$(CURDIR)/.exitcode
run-bg: init $(MAPPING_TSV) $(PAIRING_TSV) $(LOG_DIR)
	[ ! -f "$(MAPPING_TSV)" ] && echo ">>> ERROR: mapping file does not exist; $(MAPPING_TSV)" && exit 1 || :
	[ ! -f "$(PAIRING_TSV)" ] && echo ">>> ERROR: pairing file does not exist; $(PAIRING_TSV)" && exit 1 || :
	source "$(ENV)" ; \
	set +e ; \
	nextflow \
	-log "$(NXF_LOG)" \
	-c "$(TEMPO_CONFIG)" \
	run tempo/pipeline.nf \
	-resume \
	-profile juno \
	--aggregate \
	--QC \
	--genome 'GRCh37' \
	--somatic \
	--mapping "$(MAPPING_TSV)" \
	--pairing "$(PAIRING_TSV)" \
	--outDir "$(OUTPUT_DIR)" \
	-with-report "$(NXF_REPORT)" \
	-with-timeline "$(NXF_TIMELINE)" \
	-with-trace "$(NXF_TRACE)" \
	-process.clusterOptions='-sla CMOPI' \
	-N "$(EMAIL_ADDRESS)" & nxf_pid=$$! ; \
	echo "WRITING PID $$nxf_pid" ; \
	echo "$$nxf_pid" > "$(NXF_PID_FILE)" ; \
	echo "WATING FOR PID $$nxf_pid" ; \
	wait $$nxf_pid ; exitcode=$$? ; \
	echo "EXIT CODE IS:$$exitcode"; echo $$exitcode > "$(PIPELINE_EXITCODE_FILE)"

# -executor.queueSize="50"
# -process.scratch='false'

test: init $(LOG_DIR)
	source "$(ENV)" ; \
	nextflow -log "$(NXF_LOG)" \
	run tempo/pipeline.nf \
	--mapping tempo/test_inputs/local/full_test_mapping.tsv \
	--pairing tempo/test_inputs/local/full_test_pairing.tsv \
	-profile test_singularity \
	--outDir results \
	--somatic --QC --aggregate \
	-with-report "$(NXF_REPORT)" \
	-with-timeline "$(NXF_TIMELINE)" \
	-with-trace "$(NXF_TRACE)" & nxf_pid=$$! && \
	echo "$$nxf_pid" > "$(NXF_PID_FILE)" && \
	wait "$$nxf_pid"

# create an LSF submission script; SUB_SCRIPT
# - sets a submission lock file; (SUBMIT_LOCKFILE)
# - print LSF job metadata; lsf.print-env.sh
# - run Makefile recipes to record configs, start & monitor pipeline,
# - nxf_kill: propagate term signals to Nextflow pipeline so it can shutdown cleanly
# - get_pid: get the process id for the Nextflow pipeline
# - wait_pid: wait for process to stop
# - rm_submit: remove the lockfile (SUBMIT_LOCKFILE)
# - exit_1: record exit status of 1 to denote failure/termination
# - on_term: trap termination signals and run ^^^ shutdown commands and other cleanup recipes
# NOTE: Nextflow locks itself from concurrent instances but need to lock against multiple 'make submit'
# catches 'bkill' commands and propagates them up to Nextflow for clean shutdown
SUBMIT_LOCKFILE:=$(CURDIR)/.submitted
# memory usage; mem (GB) * cpus
SUB_CPUS:=2
SUB_MEM_ARG:=rusage[mem=8]
SUB_TIME:=400:00
SUB_SCRIPT:=submit.lsf.sh
SUB_RUN_RECIPE:=run-bg
SUB_EXIT_RECIPES:=check-errors calc_time jira-check-exit-state jira-upload-nextflow-report
SUB_START_RECIPES:=jira-started jira-upload-mapping jira-upload-pairing
$(SUB_SCRIPT): $(LOG_DIR)
	@echo '#!/bin/bash' > $(SUB_SCRIPT)
	@echo '#BSUB -W $(SUB_TIME)' >> $(SUB_SCRIPT)
	@echo '#BSUB -n $(SUB_CPUS)' >> $(SUB_SCRIPT)
	@echo '#BSUB -R "$(SUB_MEM_ARG)"' >> $(SUB_SCRIPT)
	@echo '#BSUB -oo $(LOG_DIR)/lsf.%J.log' >> $(SUB_SCRIPT)
	@echo 'set -x' >> $(SUB_SCRIPT)
	@echo 'cd $(CURDIR)' >> $(SUB_SCRIPT)
	@echo 'touch $(SUBMIT_LOCKFILE)' >> $(SUB_SCRIPT)
	@echo 'exit_1(){ echo ">>> exit_1"; printf 1 > "$(PIPELINE_EXITCODE_FILE)" ; }' >> $(SUB_SCRIPT)
	@echo 'on_kill(){ echo ">>> trap: on_kill"; nxf_kill; exit_1; }' >> $(SUB_SCRIPT)
	@echo 'on_term(){ echo ">>> trap: on_term" ; rm_submit; make $(SUB_EXIT_RECIPES) TIMESTAMP=$(TIMESTAMP) LOG_DIR=$(LOG_DIR); }' >> $(SUB_SCRIPT)
	@echo 'get_pid(){ head -1 $(NXF_PID_FILE); }' >> $(SUB_SCRIPT)
	@echo 'rm_submit(){ echo ">>> trap: rm_submit" ; [ -e $(SUBMIT_LOCKFILE) ] && rm -f $(SUBMIT_LOCKFILE) || : ; }' >> $(SUB_SCRIPT)
	@echo 'wait_pid(){ local pid=$$1 ; while kill -0 $$pid; do echo ">>> waiting for process $$pid to end" ; sleep 3 ; done ; }' >> $(SUB_SCRIPT)
	@echo 'nxf_kill(){ echo ">>> nxf_kill" && pid=$$(get_pid) && kill $$pid && wait_pid $$pid ; on_term; }' >> $(SUB_SCRIPT)
	@echo 'trap on_kill HUP INT KILL TERM USR1 USR2' >> $(SUB_SCRIPT)
	@echo 'trap on_term EXIT' >> $(SUB_SCRIPT)
	@echo 'bash lsf.print-env.sh' >> $(SUB_SCRIPT)
	@echo 'make config $(SUB_START_RECIPES) $(SUB_RUN_RECIPE) TIMESTAMP=$(TIMESTAMP) LOG_DIR=$(LOG_DIR)' >> $(SUB_SCRIPT)
.PHONY: $(SUB_SCRIPT)


# submit the pipeline as a job on the HPC; catch the job ID to save to file
JOB_ID_FILE:=job.id
submit: init $(MAPPING_TSV) $(PAIRING_TSV) $(LOG_DIR)
	@if [ -e "$(SUBMIT_LOCKFILE)" ]; then \
	echo ">>> ERROR: Workflow locked by $(SUBMIT_LOCKFILE); has an instance of the pipeline has already been submitted?"; exit 1 ; \
	else \
	$(MAKE) $(SUB_SCRIPT) TIMESTAMP=$(TIMESTAMP) LOG_DIR=$(LOG_DIR) && \
	bsub < $(SUB_SCRIPT) | tee >( sed -e 's|Job <\([0-9]*\)>.*|\1|g' > $(JOB_ID_FILE) ) ; \
	echo ">>> Pipeline submitted, log dir will be: $(LOG_DIR)" ; \
	fi

# check status of the leader job
check: $(JOB_ID_FILE)
	@bjobs "$$(head -1 $(JOB_ID_FILE))"

# kill the leader job or try to kill the Nextflow process id
kill:
	@if [ -e "$(SUBMIT_LOCKFILE)" ] ; then bkill "$$(head -1 $(JOB_ID_FILE))" ; \
	elif [ -e "$(NXF_PID_FILE)" ] ; then kill "$$(head -1 $(NXF_PID_FILE))" ; \
	fi ;

# check the Tempo output and logs for potential errors, record to text file
# the text file will be used in downstream processes for Jira messages
export ERROR_MESSAGE:=$(LOG_DIR)/errors.txt
check-errors: $(LOG_DIR)
	check-for-errors.sh &> "$(ERROR_MESSAGE)"

# calculate some pipeline duration metrics to log for later usages
export TRACE_TIME_FILE:=$(LOG_DIR)/duration.trace.txt
export TRACE_TIME_RAW_FILE:=$(LOG_DIR)/duration.trace.raw.txt
export SAMPLES_TIME_FILE:=$(LOG_DIR)/duration.samples.txt
export SAMPLES_TIME_RAW_FILE:=$(LOG_DIR)/duration.samples.raw.txt
calc_time: $(LOG_DIR)
	python calc_time.py trace "$(NXF_TRACE)" &> "$(TRACE_TIME_FILE)"
	python calc_time.py trace --seconds "$(NXF_TRACE)" &> "$(TRACE_TIME_RAW_FILE)"
	python calc_time.py samples "$(NXF_TRACE)" "$(MAPPING_TSV)" &> "$(SAMPLES_TIME_FILE)"
	python calc_time.py samples --seconds "$(NXF_TRACE)" "$(MAPPING_TSV)" &> "$(SAMPLES_TIME_RAW_FILE)"


# ~~~~~ JIRA INTEGRATION ~~~~~ #
JIRA_CONFIG:=$(CURDIR)/jira.json
JIRA_MESSAGE:=jira.body.json
JIRA_STARTED:=$(LOG_DIR)/jira.started.json
JIRA_SUCCESS:=$(LOG_DIR)/jira.succes.json
JIRA_FAILED:=$(LOG_DIR)/jira.failed.json
JIRA_KILLED:=$(LOG_DIR)/jira.killed.json
JIRA_CREDENTIALS_FILE:=/juno/work/ci/roslin-internal-services/Connect.txt
JIRA_USERNAME:=$(shell head -1 $(JIRA_CREDENTIALS_FILE))
JIRA_PASSWORD:=$(shell tail -n +2 $(JIRA_CREDENTIALS_FILE) | head -n 1)
JIRA_URL:=http://plvpipetrack1.mskcc.org:8090
JIRA_PROJ:=CT
JIRA_ISSUE:=
PROJECT:=$(shell head -1 "$(PROJECT_FILE)")

# create a new Jira issue on the 'CT' board for this project
$(JIRA_CONFIG): $(PROJECT_FILE)
	@curl \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	-X POST \
	--data '{"fields" : { "project": { "key": "$(JIRA_PROJ)"}, "summary": "Tempo $(PROJECT)", "issuetype": {"name" : "Task"}, "description" : "Description goes here"}}' \
	-H "Content-Type: application/json" \
	$(JIRA_URL)/rest/api/2/issue/ | tee "$(JIRA_CONFIG)" && \
	printf "\n\n>>> Jira ticket created successfully\n" || \
	echo ">>> ERROR: Something went wrong, Jira ticket may not have been created" || exit 1
# {"fields" : { "project": { "key": board}, "summary": summary, "issuetype": {"name" : "Task"},  "reporter":{"name":scruffy_username}, "assignee":{"name":assignee}, "priority":{"name": "Major"}, "description" : message}}

jira-create: $(PROJECT_FILE) $(JIRA_CONFIG)
	$(MAKE) $(JIRA_CONFIG)

# send a message that the pipeline started
jira-started: $(LOG_DIR)
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	message.py started > "$(JIRA_STARTED)"  && \
	$(MAKE) jira-comment JIRA_ISSUE=$$jira_issue JIRA_MESSAGE=$(JIRA_STARTED)

# upload files to the Jira
JIRA_UPLOAD_FILE:=
jira-upload:
	@if [ ! -e "$(JIRA_UPLOAD_FILE)" ]; then echo "ERROR: File does not exist; $(JIRA_UPLOAD_FILE)"; exit 0; fi
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	curl -H "X-Atlassian-Token: nocheck" \
	-X POST \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	-F "file=@$(JIRA_UPLOAD_FILE)" \
	$(JIRA_URL)/rest/api/2/issue/$$jira_issue/attachments

jira-upload-mapping: $(MAPPING_TSV)
	$(MAKE) jira-upload JIRA_UPLOAD_FILE=$(MAPPING_TSV)

jira-upload-pairing: $(PAIRING_TSV)
	$(MAKE) jira-upload JIRA_UPLOAD_FILE=$(PAIRING_TSV)

# TODO: should this exit with 1 or 0? Set 0 for now because dont want it to block downstream tasks
jira-upload-nextflow-report:
	if [ ! -e "$(NXF_REPORT)" ]; then echo "ERROR: Nextflow report does not exist; $(NXF_REPORT)"; exit 0; fi
	$(MAKE) jira-upload JIRA_UPLOAD_FILE=$(NXF_REPORT)

# check the exit status of the pipeline and send it to Jira
jira-check-exit-state: $(PIPELINE_EXITCODE_FILE)
	code=$$(head -1 $(PIPELINE_EXITCODE_FILE)) && \
	if [ $$code == "0" ]; then $(MAKE) jira-success ; else $(MAKE) jira-failed; fi

# send a message that the pipeline completed successfully
jira-success: $(LOG_DIR)
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	message.py success > "$(JIRA_SUCCESS)" && \
	$(MAKE) jira-comment JIRA_ISSUE=$$jira_issue JIRA_MESSAGE=$(JIRA_SUCCESS)

# send a message that the pipeline failed
jira-failed: $(LOG_DIR)
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	message.py failed > "$(JIRA_FAILED)" && \
	$(MAKE) jira-comment JIRA_ISSUE=$$jira_issue JIRA_MESSAGE=$(JIRA_FAILED)

jira-killed: $(LOG_DIR)
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	message.py killed > "$(JIRA_KILLED)" && \
	$(MAKE) jira-comment JIRA_ISSUE=$$jira_issue JIRA_MESSAGE=$(JIRA_KILLED)

jira-comment: $(JIRA_MESSAGE)
	curl -H "Content-Type: application/json" \
	-X POST \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	--data @$(JIRA_MESSAGE) \
	$(JIRA_URL)/rest/api/2/issue/$(JIRA_ISSUE)/comment

# ~~~~~ DEBUG ~~~~~ #
# interactive shell with environment populated
bash:
	source "$(ENV)" ; \
	bash

clean:
	rm -f bamMapping.tsv \
	fileTracking.tsv \
	job.id \
	.nextflow.pid
	rm -rf .nextflow

clean-all: clean
	rm -rf logs output work submit.lsf.sh
