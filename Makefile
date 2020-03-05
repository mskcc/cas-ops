SETUP_JSON:=setup.json
PROJECT:=
PIPELINE:=
ROOT:=/juno/res/ci
REMOTE:=git@github.com:mskcc/cas-ops.git
TIMESTAMP_YEARMONTH:=$(shell date +"%Y%m")
TIMESTAMP_DAY:=$(shell date +"%d_%H%M%S")
TIMESTAMP_DIR:=$(TIMESTAMP_YEARMONTH)/$(TIMESTAMP_DAY)
PROJECT_DIR:=
check-pipeline:
	@if [ -z "$(PIPELINE)" ]; then echo ">>> ERROR: 'PIPELINE' must be specified; 'make ... PIPELINE=<PIPELINE_id>'"; exit 1; fi ; \
	if [ $$(python -c 'import sys, json; print(json.load(open("$(SETUP_JSON)"))["versions"].get("$(PIPELINE)"))') == "None" ]; then \
	echo ">>> ERROR: pipeline $(PIPELINE) not in $(SETUP_JSON)" ; exit 1; fi

check-project:
	@if [ -z "$(PROJECT)" ]; then echo ">>> ERROR: 'PROJECT' must be specified; 'make ... PROJECT=<PROJECTect_id>'"; exit 1; fi

clone:
	@git clone --recurse "$(REMOTE)" "$(PROJECT_DIR)" && \
	chmod -R g+rw "$(PROJECT_DIR)" && \
	echo ">>> Project deployed to $(PROJECT_DIR)" || \
	echo ">>> ERROR: Deploy failed for PROJECTect$(PROJECT)"

# make deploy PROJECT=Proj_OCTAD PIPELINE=tempo ROOT=/juno/work/ci/trinity/runs
# /juno/work/ci/trinity/runs/202003/05_122913/Proj_OCTAD/tempo/1.2-0-g94e134a
deploy: check-project check-pipeline
	version=$$(python -c 'import json; print(json.load(open("$(SETUP_JSON)"))["versions"]["$(PIPELINE)"])') && \
	if [ -z "$(PROJECT_DIR)" ]; then project_dir="$(ROOT)/$(TIMESTAMP_DIR)/$(PROJECT)/$(PIPELINE)/$$version" ; \
	else project_dir="$(PROJECT_DIR)" ; fi ; \
	$(MAKE) clone PROJECT_DIR="$$project_dir"
