"""
Given SRX, sampleLabel, and fastq folder path, perform srr download, md5 check, fastq-dump and renaming.
Usage:
python getData.py SRX_ID SampleLabel FastqFolder pair|single
"""

import sys
import time
import os
import subprocess


srx = sys.argv[1]
sampleName = sys.argv[2]
fastq_folder = sys.argv[3]
seqType      = sys.argv[4] # can be either "pair" or "single"

# Step1: retrieve SRX associating SRR:
cmd = "esearch -db sra -query " + srx + " | efetch -format runinfo | awk 'NR%2==0' | cut -d ',' -f 1"

srrList = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode("utf-8").split("\n")
srrList = [x for x in srrList if not x == ""]

errFile = fastq_folder + "/getDataPyErr.txt"

print("Downloading SRR records with prefetch for " + srx + " ...")
for srr in srrList:
    print("Processing " + srr + " ...")
    cmd = "cd " + fastq_folder + " && bsub -q short -n 1 -W 4:00 -R rusage[mem=20480] prefetch -O ./ " + srr
    fileName = fastq_folder + "/" + srr + ".sra"

    if not os.path.isfile(fileName):
        subprocess.call(cmd, shell=True)
        sleep    = 0
        download = 0
    else:
        print(srr + " downloaded!")
        download = 1

    # check to see if downloading is complete or not:
    while (download == 0):
        print("  Sleeping " + str(sleep) + " till next check ...")
        if os.path.isfile(fileName):
            download = 1
            print(srr + " downloaded!")
        else:
            time.sleep(sleep)
            sleep = sleep + 10
        if sleep > 20000:
            print("ERROR: " + srr + " download failed!")
            f = open(errFile, "a")
            f.write("ERROR: " + srr + " download failed!\n")
            f.close()
            exit()

    # Check md5 with vdb-validate command:
    cmd = "cd " + fastq_folder + " && bsub -q short -n 1 -W 4:00 -R rusage[mem=20480] -o " + fastq_folder + "/" + srr + ".md5.log.txt" + " vdb-validate " + srr + ".sra"
    filename = fastq_folder + "/" + srr + ".md5.log.txt"
    # Check md5 check result:
    try:
        subprocess.call("rm " + filename, shell=True)
    except:
        continue
    subprocess.call(cmd, shell=True)

    md5_check = 0
    sleep     = 0
    while (md5_check == 0):
        print("Checking md5 integrity for " + srr + " ...")
        print(" Sleeping " + str(sleep) + " till next check ...")
        if os.path.isfile(filename):
            md5Complete = 0
            for line in open(filename):
                if ("The output (if any) is above this job summary." in line):
                    md5Complete = 1
            if md5Complete:
                md5_check = 1
                finished   = 0
                for line in open(filename):
                    if "is consistent" in line:
                        finished = 1
                if finished:
                    print("ERROR: md5check passed for " + srr)
                else:
                    print("ERROR: md5check failed for " + srr)
                    f = open(errFile, "a")
                    f.write("ERROR: md5check failed for " + srr + "!\n")
                    f.close()
                    exit()
        time.sleep(sleep)
        if sleep > 1000:
            print("ERROR: md5check not executed for " + srr + "!")
            f = open(errFile, "a")
            f.write("ERROR: md5check not executed for " + srr + "!\n")
            f.close()
            exit()
        sleep = sleep + 10

    # fastq-dump srr into fastq.gz files:
    # cmd = "cd " + fastq_folder + " && bsub -q short -n 1 -W 4:00 -R rusage[mem=20480] -o " + fastq_folder + "/" + srr + ".fastq_dump.log.txt" + " parallel-fastq-dump -s " + srr + ".sra -t 1 -O ./ --tmpdir ./ --split-files --gzip && rm " + srr + ".sra"
    cmd = "cd " + fastq_folder + " && bsub -q short -n 8 -W 4:00 -R rusage[mem=20480] -o " + fastq_folder + "/" + srr + ".fastq_dump.log.txt" + " parallel-fastq-dump -s " + srr + ".sra -t 8 -O ./ --tmpdir ./ --split-files --gzip"

    filename = fastq_folder + "/" + srr + ".fastq_dump.log.txt"
    try:
        subprocess.call("rm " + filename, shell=True)
    except:
        continue
    subprocess.call(cmd, shell=True)
    # print(cmd)

    dump_check = 0
    sleep     = 0
    while (dump_check == 0):
        print("Checking fastq_dump status for " + srr + " ...")
        print(" Sleeping " + str(sleep) + " till next check ...")
        if os.path.isfile(filename):
            fileComplete = 0
            for line in open(filename):
                if ("The output (if any) is above this job summary." in line):
                    fileComplete = 1
            if fileComplete:
                dump_check = 1
                finished   = 0
                for line in open(filename):
                    if "Successfully completed." in line:
                        finished = 1
                if finished:
                    print("Fastq.gz dumped for " + srr)
                else:
                    print("ERROR: fastq-dump failed for " + srr)
                    f = open(errFile, "a")
                    f.write("ERROR: fastq-dump failed for " + srr + "!\n")
                    f.close()
                    exit()
        time.sleep(sleep)
        if sleep > 3600:
            print("ERROR: fastq-dump not executed for " + srr + "!")
            f = open(errFile, "a")
            f.write("ERROR: fastq-dump not executed for " + srr + "!\n")
            f.close()
            exit()
        sleep = sleep + 10

# concatenate/rename fastq.gz files

## determine SE or PE:
# test = srrList[0]
# testR2 = fastq_folder + "/" + test + ".*2.fastq.gz"
# print(testR2)

# if PE:
# if os.path.isfile(testR2):
if (seqType == "pair"):
    print("Renaming PE fastq.gz files ...")
    temR1 = [item + "\*1.fastq.gz" for item in srrList]
    tem_filesR1 = " ".join(temR1)
    cmdR1 = "cat " + tem_filesR1 + " > " + sampleName + ".R1.fastq.gz.log"

    temR2 = [item + "\*2.fastq.gz" for item in srrList]
    tem_filesR2 = " ".join(temR2)
    cmdR2 = "cat " + tem_filesR2 + " > " + sampleName + ".R2.fastq.gz.log"

    cmd = "cd " + fastq_folder + " && bsub -q short -n 1 -W 4:00 -R rusage[mem=20480] -o " + fastq_folder + "/" + sampleName + ".R1.fastq.gz " + cmdR1
    subprocess.call(cmd, shell=True)
    print(cmd)

    cmd = "cd " + fastq_folder + " && bsub -q short -n 1 -W 4:00 -R rusage[mem=20480] -o " + fastq_folder + "/" + sampleName + ".R2.fastq.gz " + cmdR2
    subprocess.call(cmd, shell=True)
    print(cmd)
# if SE:
elif (seqType == "single"):
    print("Renaming SE fastq.gz files ...")
    temR1 = [item + "\*.fastq.gz" for item in srrList]
    tem_filesR1 = " ".join(temR1)
    cmdR1 = "cat " + tem_filesR1 + " > " + fastq_folder + "/" + sampleName + ".R1.fastq.gz.log"

    cmd = "cd " + fastq_folder + " && bsub -q short -n 1 -W 4:00 -R rusage[mem=20480] -o " + fastq_folder + "/" + sampleName + ".R1.fastq.gz " + cmdR1

    print(cmd)
    subprocess.call(cmd, shell=True)

# clean intermediate data:
cmd = "cd " + fastq_folder + " && rm *.sra"
subprocess.call(cmd, shell=True)
print("getData.py finished for " + srx + "!")
