# Tempo Pipeline

Scripts to setup and run Tempo pipeline. 

# Usage

1. Create `mapping.tsv` and `pairing.tsv` in this directory (see examples in `example` dir)

2. Run `make run` to run in the current session, or `make submit` to submit the pipeline to LSF (configured for Juno HPC cluster)

## Extras

- `make submit RECIPE=test`: submit a test-run of the Tempo pipeline to LSF

- `make kill`: kill a submitted pipeline (allows for clean Nextflow shutdown of child jobs)

# Output

Logs will be saved in a time-stamped directory under `logs`

Output files will be saved in the directory `output`
