SHELL:=/bin/bash
UNAME:=$(shell uname)
HOSTNAME:=$(shell hostname)
TIMESTAMP:=$(shell date +"%Y-%m-%d_%H-%M-%S")
LOG_DIR:=$(CURDIR)/logs/$(TIMESTAMP)
export NXF_ANSI_LOG:=false
export NXF_VER:=19.10.0
export NXF_WORK:=$(CURDIR)/work
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
	mkdir -p "$(LOG_DIR)"

init: ./nextflow tempo $(LOG_DIR)


# ~~~~~ RUN ~~~~~ #
MAPPING_TSV:=$(CURDIR)/mapping.tsv
PAIRING_TSV:=$(CURDIR)/pairing.tsv
OUTPUT_DIR:=$(CURDIR)/output
run: init $(MAPPING_TSV) $(PAIRING_TSV)
	[ ! -f "$($(MAPPING_TSV))" ] && echo ">>> ERROR: mapping file does not exist; $(MAPPING_TSV)" && exit 1 || :
	[ ! -f "$($(PAIRING_TSV))" ] && echo ">>> ERROR: pairing file does not exist; $(PAIRING_TSV)" && exit 1 || :
	source "$(ENV)" ; \
	nextflow run tempo/pipeline.nf \
	-log "$(NXF_LOG)" \
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
	-with-trace "$(NXF_TRACE)" | \
	tee -a "$(STDOUT_LOG)"

# create an LSF submission script
# memory usage; mem (GB) * cpus
SUB_CPUS:=2
SUB_MEM_ARG:=rusage[mem=8]
SUB_TIME:=120:00
SUB_SCRIPT:=submit.lsf.sh
$(SUB_SCRIPT):
	echo '#!/bin/bash' > $(SUB_SCRIPT)
	echo '#BSUB -W $(SUB_TIME)' >> $(SUB_SCRIPT)
	echo '#BSUB -n $(SUB_CPUS)' >> $(SUB_SCRIPT)
	echo '#BSUB -R "$(SUB_MEM_ARG)"' >> $(SUB_SCRIPT)
	echo '#BSUB -oo $(LOG_DIR)/%J.log' >> $(SUB_SCRIPT)
	echo 'set -eux' >> $(SUB_SCRIPT)
	echo 'cd $(CURDIR)' >> $(SUB_SCRIPT)
	echo 'make run' >> $(SUB_SCRIPT)
.PHONY: $(SUB_SCRIPT)

# submit the pipeline as a job on the HPC; catch the job ID to save to file
JOB_ID_FILE:=job.id
submit: $(SUB_SCRIPT) $(LOG_DIR)
	bsub < $(SUB_SCRIPT) | tee >( sed -e 's|Job <\([0-9]*\)>.*|\1|g' > $(JOB_ID_FILE) )


# ~~~~~ DEBUG ~~~~~ #
# interactive shell with environment populated
bash:
	source "$(ENV)" ; \
	bash
