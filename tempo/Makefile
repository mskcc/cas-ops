define help
This is the Makefile for CAS-OPS Tempo analysis

This directory should have been 'deployed' from a copy of the Makefile in the parent directory.

Create a Jira ticket with:

make jira-create

Then submit the pipeline with:

make submit

endef
export help
help:
	@printf "$$help"
.PHONY : help

SHELL:=/bin/bash
UNAME:=$(shell uname)
HOSTNAME:=$(shell hostname)
TIMESTAMP:=$(shell date +"%Y-%m-%d_%H-%M-%S")
EMAIL_USER:=$(shell whoami)
EMAIL_HOST:=mskcc.org
EMAIL_ADDRESS:=$(EMAIL_USER)@$(EMAIL_HOST)
EXTERNAL_CONFIG:=../config.json
CONFIG_TEMPLATE:=.config.json
CONFIG_JSON:=config.json
export LOG_DIR:=$(CURDIR)/logs/$(TIMESTAMP)
export NXF_ANSI_LOG:=false
export NXF_VER:=19.10.0
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
export TEMPO_COMMIT:=94e134a
export TEMPO_TAG:=1.2.0
tempo:
	git clone git@github.com:mskcc/tempo.git && cd tempo && git checkout "$(TEMPO_TAG)"

$(LOG_DIR):
	@mkdir -p "$(LOG_DIR)"

# initialize the local dir for pipeline execution
init: ./nextflow tempo $(LOG_DIR)

# save a local config file so we can more easily retrieve some execution values later
$(CONFIG_JSON): $(CONFIG_TEMPLATE)
	cp "$(CONFIG_TEMPLATE)" "$(CONFIG_JSON)"

# TODO: come up with a better way of handling this; wish we could use jq but its not installed by default...
config: $(CONFIG_JSON)
	@[ -n "$(TIMESTAMP)" ] && sed -i -e 's|timestamp_goes_here|$(TIMESTAMP)|g' $(CONFIG_JSON) || :
	@[ -n "$(LOG_DIR)" ] && sed -i -e 's|log_dir_goes_here|$(LOG_DIR)|g' $(CONFIG_JSON) || :

# ~~~~~ RUN ~~~~~ #
MAPPING_TSV:=$(CURDIR)/mapping.tsv
PAIRING_TSV:=$(CURDIR)/pairing.tsv
OUTPUT_DIR:=$(CURDIR)/output

# run in the current process
run: init $(MAPPING_TSV) $(PAIRING_TSV)
	[ ! -f "$(MAPPING_TSV)" ] && echo ">>> ERROR: mapping file does not exist; $(MAPPING_TSV)" && exit 1 || :
	[ ! -f "$(PAIRING_TSV)" ] && echo ">>> ERROR: pairing file does not exist; $(PAIRING_TSV)" && exit 1 || :
	source "$(ENV)" ; \
	nextflow -log "$(NXF_LOG)" \
	run tempo/pipeline.nf \
	-resume \
	-profile juno \
	--genome 'GRCh37' \
	--somatic \
	--germline \
	--mapping "$(MAPPING_TSV)" \
	--pairing "$(PAIRING_TSV)" \
	--outDir "$(OUTPUT_DIR)" \
	-with-report "$(NXF_REPORT)" \
	-with-timeline "$(NXF_TIMELINE)" \
	-with-trace "$(NXF_TRACE)"
	# | \
	# tee -a "$(STDOUT_LOG)"

# run in the background; capture Nextflow process ID and save to file
# use this for running inside an LSF job where you need to pass
# KILL signal to Nextflow for clean shutdown
run-bg: init $(MAPPING_TSV) $(PAIRING_TSV)
	[ ! -f "$(MAPPING_TSV)" ] && echo ">>> ERROR: mapping file does not exist; $(MAPPING_TSV)" && exit 1 || :
	[ ! -f "$(PAIRING_TSV)" ] && echo ">>> ERROR: pairing file does not exist; $(PAIRING_TSV)" && exit 1 || :
	source "$(ENV)" ; \
	nextflow -log "$(NXF_LOG)" \
	run tempo/pipeline.nf \
	-resume \
	-profile juno \
	--genome 'GRCh37' \
	--somatic \
	--germline \
	--mapping "$(MAPPING_TSV)" \
	--pairing "$(PAIRING_TSV)" \
	--outDir "$(OUTPUT_DIR)" \
	-with-report "$(NXF_REPORT)" \
	-with-timeline "$(NXF_TIMELINE)" \
	-with-trace "$(NXF_TRACE)" \
	-N "$(EMAIL_ADDRESS)" & nxf_pid=$$! && \
	echo "$$nxf_pid" > "$(NXF_PID_FILE)" && \
	wait %1 ; echo $$? > "$(PIPELINE_EXITCODE_FILE)"

test: init
	source "$(ENV)" ; \
	nextflow -log "$(NXF_LOG)" \
	run tempo/pipeline.nf \
	--mapping tempo/test_inputs/local/full_test_mapping.tsv \
	--pairing tempo/test_inputs/local/full_test_pairing.tsv \
	-profile test_singularity \
	--outDir results \
	--somatic --germline --QC --aggregate \
	-with-report "$(NXF_REPORT)" \
	-with-timeline "$(NXF_TIMELINE)" \
	-with-trace "$(NXF_TRACE)" & nxf_pid=$$! && \
	echo "$$nxf_pid" > "$(NXF_PID_FILE)" && \
	wait "$$nxf_pid"

# create an LSF submission script
# sets a submission lock file
# NOTE: Nextflow locks itself from concurrent instances but need to lock against multiple 'make submit'
# catches 'bkill' commands and propagates them up to Nextflow for clean shutdown
SUBMIT_LOCKFILE:=$(CURDIR)/.submitted
PIPELINE_EXITCODE_FILE:=$(CURDIR)/.exitcode
# memory usage; mem (GB) * cpus
SUB_CPUS:=2
SUB_MEM_ARG:=rusage[mem=8]
SUB_TIME:=120:00
SUB_SCRIPT:=submit.lsf.sh
RECIPE:=jira-started jira-upload run-bg jira-check-exit-state
$(SUB_SCRIPT):
	@echo '#!/bin/bash' > $(SUB_SCRIPT)
	@echo '#BSUB -W $(SUB_TIME)' >> $(SUB_SCRIPT)
	@echo '#BSUB -n $(SUB_CPUS)' >> $(SUB_SCRIPT)
	@echo '#BSUB -R "$(SUB_MEM_ARG)"' >> $(SUB_SCRIPT)
	@echo '#BSUB -oo $(LOG_DIR)/%J.log' >> $(SUB_SCRIPT)
	@echo 'set -eux' >> $(SUB_SCRIPT)
	@echo 'cd $(CURDIR)' >> $(SUB_SCRIPT)
	@echo 'touch $(SUBMIT_LOCKFILE)' >> $(SUB_SCRIPT)
	@echo 'get_pid(){ head -1 $(NXF_PID_FILE); }' >> $(SUB_SCRIPT)
	@echo 'rm_submit(){ echo ">>> trap: rm_submit" ; [ -e $(SUBMIT_LOCKFILE) ] && rm -f $(SUBMIT_LOCKFILE) || : ; }' >> $(SUB_SCRIPT)
	@echo 'wait_pid(){ local pid=$$1 ; while kill -0 $$pid; do echo waiting for process $$pid to end ; sleep 1 ; done ; }' >> $(SUB_SCRIPT)
	@echo 'nxf_kill(){ rm_submit ; echo ">>> trap: nxf_kill" && pid=$$(get_pid) && kill $$pid && wait_pid $$pid ; }' >> $(SUB_SCRIPT)
	@echo 'trap nxf_kill HUP' >> $(SUB_SCRIPT)
	@echo 'trap nxf_kill INT' >> $(SUB_SCRIPT)
	@echo 'trap nxf_kill EXIT' >> $(SUB_SCRIPT)
	@echo 'bash lsf.print-env.sh' >> $(SUB_SCRIPT)
	@echo 'make config $(RECIPE) TIMESTAMP=$(TIMESTAMP) LOG_DIR=$(LOG_DIR)' >> $(SUB_SCRIPT)

.PHONY: $(SUB_SCRIPT)
# ; echo $$? > $(PIPELINE_EXITCODE_FILE)
# @echo 'make jira-check-exit-state' >> $(SUB_SCRIPT)
# TODO: get this ^ to work so we can catch the pipeline exit code and store it for later evaluation

# submit the pipeline as a job on the HPC; catch the job ID to save to file
JOB_ID_FILE:=job.id
submit: init $(MAPPING_TSV) $(PAIRING_TSV)
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


# ~~~~~ JIRA INTEGRATION ~~~~~ #
JIRA_CONFIG:=$(CURDIR)/jira.json
JIRA_MESSAGE:=body.json
JIRA_CREDENTIALS_FILE:=/juno/work/ci/roslin-internal-services/Connect.txt
JIRA_USERNAME:=$(shell head -1 $(JIRA_CREDENTIALS_FILE))
JIRA_PASSWORD:=$(shell tail -n +2 $(JIRA_CREDENTIALS_FILE) | head -n 1)
JIRA_URL:=http://plvpipetrack1.mskcc.org:8090
JIRA_PROJ:=CT
PROJECT:=
# make sure ../config.json exists from deploy step in order to retrieve project
check-config:
	if [ ! -e "$(EXTERNAL_CONFIG)" ]; then echo ">>> ERROR: Config file $(EXTERNAL_CONFIG) does not exist; was this project created with 'make deploy'?" ; exit 1 ; fi

# create a new Jira issue on the 'CT' board for this project
$(JIRA_CONFIG): check-config
	@curl \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	-X POST \
	--data '{"fields" : { "project": { "key": "$(JIRA_PROJ)"}, "summary": "Tempo $(PROJECT)", "issuetype": {"name" : "Task"}, "description" : "Description goes here"}}' \
	-H "Content-Type: application/json" \
	$(JIRA_URL)/rest/api/2/issue/ | tee "$(JIRA_CONFIG)" && \
	printf "\n\n>>> Jira ticket created successfully\n" || \
	echo ">>> ERROR: Something went wrong, Jira ticket may not have been created" || exit 1
# {"fields" : { "project": { "key": board}, "summary": summary, "issuetype": {"name" : "Task"},  "reporter":{"name":scruffy_username}, "assignee":{"name":assignee}, "priority":{"name": "Major"}, "description" : message}}

jira-create:
	@if [ ! -e "$(JIRA_CONFIG)" ]; then \
	project=$$(python -c 'import json; print(json.load(open("$(EXTERNAL_CONFIG)"))["project"])') && \
	$(MAKE) $(JIRA_CONFIG) PROJECT=$$project ; \
	fi

# send a message that the pipeline started
jira-started:
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	curl -H "Content-Type: application/json" \
	-X POST \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	--data '{"body":"Started running pipeline in directory:\n$(CURDIR)\n\nlog dir:\n$(LOG_DIR)\n\nNextflow log:\n$(NXF_LOG)"}' \
	$(JIRA_URL)/rest/api/2/issue/$$jira_issue/comment

# upload mapping files to the Jira
jira-upload:
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	curl -H "X-Atlassian-Token: nocheck" \
	-X POST \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	-F "file=@$(MAPPING_TSV)" \
	-F "file=@$(PAIRING_TSV)" \
	$(JIRA_URL)/rest/api/2/issue/$$jira_issue/attachments

# check the exit status of the pipeline and send it to Jira
jira-check-exit-state: $(PIPELINE_EXITCODE_FILE)
	code=$$(head -1 $(PIPELINE_EXITCODE_FILE)) && \
	if [ $$code == "0" ]; then $(MAKE) jira-success ; else $(MAKE) jira-failed; fi

# send a message that the pipeline completed successfully
jira-success:
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	log_dir=$$(python -c 'import json; print(json.load(open("$(CONFIG_JSON)"))["log_dir"])') && \
	python -c "import json; json.dump({'body':'Pipeline finished successfully in directory:\n$(CURDIR)\n\nlog dir:\n$$log_dir\n\nNextflow log:\n$(NXF_LOG)'}, open('$(JIRA_MESSAGE)', 'w'))" && \
	curl -H "Content-Type: application/json" \
	-X POST \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	--data @$(JIRA_MESSAGE) \
	$(JIRA_URL)/rest/api/2/issue/$$jira_issue/comment

# send a message that the pipeline failed
jira-failed:
	@jira_issue=$$(python -c "import json; data=json.load(open('$(JIRA_CONFIG)')); print(data['key'])") && \
	log_dir=$$(python -c 'import json; print(json.load(open("$(CONFIG_JSON)"))["log_dir"])') && \
	python -c "import json; json.dump({'body':'Pipeline failed in directory:\n$(CURDIR)\n\nlog dir:\n$$log_dir\n\nNextflow log:\n$(NXF_LOG)'}, open('$(JIRA_MESSAGE)', 'w'))" && \
	curl -H "Content-Type: application/json" \
	-X POST \
	-u "$(JIRA_USERNAME):$(JIRA_PASSWORD)" \
	--data @$(JIRA_MESSAGE) \
	$(JIRA_URL)/rest/api/2/issue/$$jira_issue/comment

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
