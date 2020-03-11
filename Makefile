define help
This is the Makefile for CAS-OPS management

A master copy of this repo should live in a common location on the filesystem

'Deploy' a new analysis from this repo with a command like this:

make deploy PROJECT=Important_Samples PIPELINE=tempo

Then 'cd' over to the newly deployed project directory, then into the subdir for the desired analysis, to start.

See instructions in the subdirs for analysis-specific instructions ('make help')
endef
export help
help:
	@printf "$$help"
.PHONY : help

SETUP_JSON:=setup.json
CONFIG_TEMPLATE:=.config.json
CONFIG_JSON:=config.json
PROJECT:=
PIPELINE:=
VERSION:=
ROOT:=/juno/res/ci
REMOTE:=git@github.com:mskcc/cas-ops.git
TIMESTAMP_YEARMONTH:=$(shell date +"%Y%m")
TIMESTAMP_DAY:=$(shell date +"%d_%H%M%S")
TIMESTAMP_DIR:=$(TIMESTAMP_YEARMONTH)/$(TIMESTAMP_DAY)
PROJECT_DIR:=
# make sure that 'PIPELINE' var was passed, and that it is a valid registered pipeline in the included setup.json
check-pipeline:
	@if [ -z "$(PIPELINE)" ]; then echo ">>> ERROR: 'PIPELINE' must be specified; 'make ... PIPELINE=<PIPELINE_id>'"; exit 1; fi ; \
	if [ $$(python -c 'import sys, json; print(json.load(open("$(SETUP_JSON)"))["versions"].get("$(PIPELINE)"))') == "None" ]; then \
	echo ">>> ERROR: pipeline $(PIPELINE) not in $(SETUP_JSON)" ; exit 1; fi

# make sure that a 'PROJECT' var was passed
check-project:
	@if [ -z "$(PROJECT)" ]; then echo ">>> ERROR: 'PROJECT' must be specified; 'make ... PROJECT=<PROJECTect_id>'"; exit 1; fi

# clone a copy of the repo to the desired output location and fix the permissions
clone:
	@git clone --recurse "$(REMOTE)" "$(PROJECT_DIR)" && \
	chmod -R g+rw "$(PROJECT_DIR)" && \
	printf "\n\n>>> Project deployed to $(PROJECT_DIR)\n\n" || \
	echo ">>> ERROR: Deploy failed for PROJECTect$(PROJECT)"

# set up a new analysis in the desired location
deploy: check-project check-pipeline
	@version=$$(python -c 'import json; print(json.load(open("$(SETUP_JSON)"))["versions"]["$(PIPELINE)"])') && \
	if [ -z "$(PROJECT_DIR)" ]; then project_dir="$(ROOT)/$(TIMESTAMP_DIR)/$(PROJECT)/$(PIPELINE)/$$version" ; \
	else project_dir="$(PROJECT_DIR)" ; fi ; \
	$(MAKE) clone PROJECT_DIR="$$project_dir" && \
	$(MAKE) config CONFIG_JSON="$$project_dir/config.json" VERSION="$$version"
# $ make deploy PROJECT=Proj_OCTAD PIPELINE=tempo ROOT=/juno/work/ci/trinity/runs
# /juno/work/ci/trinity/runs/202003/05_122913/Proj_OCTAD/tempo/1.2-0-g94e134a

# copy over the template config.json file to the final config file for usage with the analysis
$(CONFIG_JSON): $(CONFIG_TEMPLATE)
	@echo ">>> Creating config file: $(CONFIG_JSON)" && \
	cp "$(CONFIG_TEMPLATE)" "$(CONFIG_JSON)"

# update the values in the config.json for use with the analysis; this is required for downstream steps in analysis subdirs !!
# TODO: come up with a better way of handling this; wish we could use jq but its not installed by default...
# NOTE: sed -i does not work on macOS you need sed -i ''
config: $(CONFIG_JSON)
	@echo ">>> Updating config file $(CONFIG_JSON)"
	@[ -n "$(PIPELINE)" ] && sed -i -e 's|pipeline_goes_here|$(PIPELINE)|g' $(CONFIG_JSON) || :
	@[ -n "$(PROJECT)" ] && sed -i -e 's|project_goes_here|$(PROJECT)|g' $(CONFIG_JSON) || :
	@[ -n "$(VERSION)" ] && sed -i -e 's|version_goes_here|$(VERSION)|g' $(CONFIG_JSON) || :
