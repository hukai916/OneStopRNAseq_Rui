#!/bin/bash
# bsub -q long -W 144:00 -R rusage[mem=4000]  'bash submit.sh'

rm -f lsf.log
source activate osr-base > workflow.log  2>&1


snakemake -p -k --jobs 99 \
--use-conda --conda-prefix ~/miniconda3/envs/osr_envs \
--latency-wait 120 --ri --restart-times 0 \
--cluster 'bsub -q short -o lsf.log -R "rusage[mem={resources.mem_mb}]" -n {threads} -R span[hosts=1] -W 4:00' >> workflow.log  2>&1 

snakemake -p -k --jobs 99 \
--use-conda --conda-prefix ~/miniconda3/envs/osr_envs \
--latency-wait 120 --ri --restart-times 1 \
--cluster 'bsub -q long -o lsf.log -R "rusage[mem={resources.mem_mb}]" -n {threads} -R span[hosts=1] -W 140:00' \
--cluster-cancel bkill \
>> workflow.2.log  2>&1 

snakemake -j 1 --report report.html > report.log  2>&1
