PY ?= python3
export PYTHONPATH := $(CURDIR)/src

.PHONY: help install test smoke prepare experiments uncertainty freeze external report all clean \
        revision revision-offline manuscript

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

install:       ## install the package and dependencies
	$(PY) -m pip install -e .[dev]

test:          ## run the test suite
	$(PY) -m pytest tests -q

smoke:         ## fast end-to-end wiring check
	$(PY) -m hoproj.pipeline.run_all --smoke

prepare:       ## R7-R10: build the modelling dataset
	$(PY) -m hoproj.pipeline.stage01_prepare

experiments:   ## R11-R13: main, leakage and ablation grids
	$(PY) -m hoproj.pipeline.stage02_experiment --experiment main
	$(PY) -m hoproj.pipeline.stage02_experiment --experiment leakage_study
	$(PY) -m hoproj.pipeline.stage02_experiment --experiment ablation_features
	$(PY) -m hoproj.pipeline.stage02_experiment --experiment multitask

uncertainty:   ## R14: ensemble, calibration, conformal, OOD, abstention
	$(PY) -m hoproj.pipeline.stage03_uncertainty --model gru

freeze:        ## record the frozen protocol before touching the external route
	$(PY) -m hoproj.pipeline.stage04_external --freeze --model gru

external:      ## R15: locked external-route evaluation (requires freeze)
	$(PY) -m hoproj.pipeline.stage04_external --model gru

report:        ## R16: consolidated thesis report
	$(PY) -m hoproj.pipeline.stage05_report

all: prepare experiments uncertainty report  ## v1 study only - see 'revision' below

# ---------------------------------------------------------------------------
# The revision (stages 22-31).  Everything the thesis actually reports lives
# here.  Stages 1-21 above are the PRE-AUDIT study, kept because Chapter 5
# quotes its numbers as the result the alignment audit overturned; running
# 'make all' alone reproduces a retracted result.
# ---------------------------------------------------------------------------
revision:      ## stages 22-31: the audit, the lag, LOCO, and every Chapter 5 number
	$(PY) -m hoproj.pipeline.run_revision

revision-offline:  ## the same, skipping the stage that downloads the NUWiNS corpus
	$(PY) -m hoproj.pipeline.run_revision --offline

manuscript:    ## rebuild the .docx from reports_rev, then verify every number in it
	cd ../Docs/manuscript-src/revision && $(PY) build_revised.py && $(PY) verify.py

clean:         ## remove generated data, artefacts and reports
	rm -rf data/interim data/processed artifacts reports
