#!/bin/bash
# run with: nohup bash submit.sh &

module purge
module load singularity/singularity-current > nohup.out   2>&1 
source activate osr >> nohup.out  2>&1 

snakemake -p -k --jobs 999 \
--use-singularity \
--use-conda \
--latency-wait 300 \
--cluster 'bsub -q long -o lsf.log -R "rusage[mem={params.mem_mb}]" -n {threads} -R span[hosts=1] -W 144:00' >> nohup.out  2>&1 

# Rui Note: 2020/06/03/18:21
# Most works with singularity
# rMAT needs py2.7, thus --use-conda necessary, skip to remove conda download overhead

snakemake --report report.html > report.log  2>&1

bsub -W 4:00 -q short "[ -d 'gsea/' ] && rm -f gsea/gsea.tar.gz && tar cf - gsea/  | pigz -p 2 -f > gsea.tar.gz && mv gsea.tar.gz gsea"


## Handy commands for development
# rm -rf lsf.log nohup.out meta/read_length.txt   meta/strandness.detected.txt log/ Workflow_DAG.all.svg     may*  DESeq2/ gsea/ report.html bigWig/ feature_count/ bam_qc/ rMATS*/
# bkill -r rl44w 0
# snakemake --unlock -j 1 
# snakemake -np -j 1 
# snakemake -nq -j 1 
# snakemake --export-cwl workflow.cwl
# mv DESeq2/ mapped_reads/ sorted_reads/ feature_count/ bigWig/ bam_qc/ fastqc/ trash

# Kai
# cd let analysis_1
# source /home/rl44w/anaconda3/etc/profile.d/conda.sh
# conda activate osr
# snakemake --use-conda -k -p --jobs 999 --latency-wait 300 --cluster ’bsub -q short -o lsf.log -R ‘rusage[mem={params.mem_mb}]’ -n {threads} -R span[hosts=1] -W 4:00' > log.snakemake.txt 2>&1 && snakemake --report report.html
# touch /home/kh45w/project/umw_hira_goel/OneStopRNAseq/users/89/Example_study1_02.22.06-05.28.2020/log_ssh2/analysis1.txt

