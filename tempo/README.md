# Tempo Pipeline

Scripts to setup and run Tempo pipeline. 

# Usage

1. Create `mapping.tsv` and `pairing.tsv` in this directory (see examples in `example` dir)

2. Run `make run` to run in the current session, or `make submit` to submit the pipeline to LSF (configured for Juno HPC cluster)

## Extras

- `make submit RECIPE=test`: submit a test-run of the Tempo pipeline to LSF

- `make kill`: kill a submitted pipeline (allows for clean Nextflow shutdown of child jobs)

# Jira Integration

To create a new Issue on the Jira board for this project, use:

```
make jira-create
```

This will save a file in the current directory, `jira.json`, which contains the identifier for the Jira ticket associated with this pipeline run. This file is required for the following Jira operations:

- `make jira-started`: Leave a message on the Jira Issue noting that the pipeline has started

- `make jira-success`: Leave a message on the Jira Issue noting a successful pipeline run

- `make jira-failed`: Leave a message on the Jira issue noting a failed pipeline

- `make jira-upload`: Upload the mapping and pairing files to the Jira Issue

# Output

Logs will be saved in a time-stamped directory under `logs`

Output files will be saved in the directory `output`
