#!/bin/bash
# for LSF system only
# bsub -q long -W 144:00 -R rusage[mem=4000]  -R select[rh=8] 'bash submit.sh'

rm -f lsf.log
source activate ~/anaconda3/envs/osr-base2  > workflow.log  2>&1

snakemake -p -k --jobs 99 \
--use-conda --conda-prefix ~/anaconda3/envs/osr_envs2 \
--latency-wait 120 --ri --restart-times 2 \
--cluster 'bsub -q long -o lsf.log -R "rusage[mem={resources.mem_mb}]" -n {threads} -R span[hosts=1] -R select[rh=8] -W 140:00' \
--cluster-cancel bkill \
>> workflow.log  2>&1 

snakemake -j 1 --report report.html > report.log  2>&1
