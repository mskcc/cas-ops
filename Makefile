export PROJ:=
export PROD_DIR:=/juno/res/ci
export PROJ_DIR:=$(PROD_DIR)/$(PROJ)
export REMOTE:=git@github.com:mskcc/cas-ops.git
deploy:
	@if [ -z "$(PROJ)" ]; then echo ">>> ERROR: 'PROJ' must be specified; make deploy PROJ=<project_id>"; exit 1; fi
	@git clone --recurse "$(REMOTE)" "$(PROJ_DIR)" && \
	echo ">>> Project deployed to $(PROJ_DIR)" || \
	echo ">>> ERROR: Deploy failed for project$(PROJ)"
