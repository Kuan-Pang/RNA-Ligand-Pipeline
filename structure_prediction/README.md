# Structure Prediction

This folder includes scripts and instruction on the workflow of predicting structure using DeepFoldRNA, and the downstream evaluation on the predicted models using RNAalign and R language.

This workflow is referenced to [DeepFoldRNA](https://www.biorxiv.org/content/10.1101/2022.05.15.491755v1) and [RNAalign](https://pubmed.ncbi.nlm.nih.gov/31161212/).

## Setup DeepFoldRNA
* Install DeepFoldRNA onto cluster by cloning their [GitHub repo](https://github.com/robpearc/DeepFoldRNA)
* Follow the instructions in the repo to download the required programs and databases

## Setup RNAalign
* Download RNAalign program from [Zhang Lab Website](https://seq2fun.dcmb.med.umich.edu//RNA-align/download.html)

## Technical settings
The jobs were done on DC cluster with total 8 nodes, each has 68 Cores, 272 threads, 200GB RAM, latest CentOS7.

## Predicting RNA structures using DeepFoldRNA
An automatic bash script for submiting jobs in batch to clusters is included in this directory. Note that the input fasta files must be named as seq.fasta for all sequences, and been placed in individual folders, for example, if the riboswitch is named as 2cky, then there should be a folder named 2cky, and only contains a filed named "seq.fasta" within this folder, containing the fasta format sequence of the riboswitch.

The following would illustrate the steps we performed in predictin riboswitch structures for this project.

First, within DeepFoldRNA directory, generate a folder that contains all the fasta files in corresponding individual folders. In our project, this folder is called "unique_fasta".

``` sh
cd unique_fasta
```

Then, list all riboswitch folders' absolute paths in a file called "fasta_list.txt" by running the following command:
``` sh
find $PWD -name "[0-9]*" -type d > fasta_list.txt
```
Since our riboswitche names follows a specific pattern that starts with integers and followed by other characters, we can use the regex pattern to list these folders.

Then go back to parent folder:
``` sh
cd ../
```

From personal understanding, DC cluster has not implemented the Job Array feature. Thus, we wrote a script to perform the same function as the Job Array feature, which automatically submits jobs to the cluster to be processed.

In the "job_array.script" file, change the "input" variable to be the path to the "fasta_list.txt" file that we just generated. In our project, the input path is "/home/zhanglab3/syzhang/DeepFoldRNA/unique_fasta/fasta_list.txt". This would be the jobs that the script would read from to predict the models. After input variable is assigned, we can run the following command to send all jobs in batch to the DC cluster:
``` sh
submitjob -n DeepFoldRNA_jobs -m 164 -c 8 -w 72 ./job_array.script
```
where "submitjob" is the command used in DC cluster to submit a job script, the -n flag indicates the name of the job array; -m flag indicates memory allocated, in this case, 164G; -c indicates number of CPUs allocated; -w is the walltime for the job to be processed.

Now the jobs for prediction are sent to the cluster. It would take 1 day per sequence on average to be predicted, so the following steps should only be performed after the submitted jobs are all completed.

## Evaluation on Prediction using RNAalign
Once all prediction steps are finished, we now obtained 6 models predicted per riboswitch sequence by DeepFoldRNA, and we would want to align them to their true structures obtained from Protein Data Bank (PDB) to calculate RMSD and TM scores to evaluate on its prediction accuracy.

First, go to our "DeepFoldRNA/unique_fasta/" directory:
``` sh
cd DeepFoldRNA/unique_fasta
```
Generate a bash script called "check_empty.script" to check whethere the folders containing the predicted models are all non-empty. If there are empty folders, then these folders should be eliminated for calculating RMSD and TM score. In our project, this folder has already been generated.
``` sh
./check_empty.script
```

This script would generate the following files:
* __**finished_models.txt: **__ Absolute path to the folders of the predicted 6 models of each sequence.
* __**final_models.txt: **__ Absolute path to the "final_models" directories within the predicted 6 models of each sequence
* __**is_empty.txt: **__ Absolute path of the folders that are empty (i.e. no models were generated for this sequence). These ones would be deleted from __**final_models.txt**__.

The __**final_models.txt**__ would be the file required for RNAalign process.

Now we move to the RNAalign directory:
``` sh
cd ../../RNAalign
```

We wrote a script called "generate_complete_list.script" to generate the absolute path to all pdb files predicted by DeepFoldRNA from "final_models.txt". The completed paths are listed in the "complete_list.txt" file. 
``` sh
./generate_complete_list.script
```

Then, we made a folder called "true_structures" to contain the riboswitch structures extracted from PDB. We will download the structures in batch using the script named as "batch_download.sh", and we need to prepare a text file containing the PDB ids that we would like to download, separated by comma. The PDB ids are stored in the "comma_fasta.txt" file. We can run the following command to download all structures:
``` sh
cd true_structures
./batch_download.sh -f comma_fasta.txt
cd ../
```
In the RNAalign directory, we also included the script to perform evaluation on all the predicted models, named as "evaluation.script". We first make a folder to save the outputs from RNAalign:
``` sh
mkdir pbs_outputs
```

Then run the evaluation script:
``` sh
./evaluation.script
```

The results would be saved in the "pbs_outputs" directory.

Now we move to "pbs_outputs" directory, and modify the RNAalign output files to only contain the lines with RMSD and TM score data. We already included the script in this folder to automate the process, named "modify_lines.script". We can run this file:
``` sh
cd pbs_outputs
./modify_lines.script
```
The modified files would be saved in the "modified" folder created within the script.

Now we go to the "modified" directory, and create a script called "generate_table.script" with the following code:
``` sh
#!/bin/bash

while read p;
do
 # Get name from the file name
 name=${p:2:9}
 
 # The two lines in the file
 line1=`head -n 1 ${p}`
 line2=`tail -n 1 ${p}`

 # Get RMSD from line 1 of the file
 RMSD=${line1:28:4}

 # Get TM from line 2 of the file
 TM=${line2:10:7}
 
 # Append to the pbs_output_table.txt
 echo "${name},${RMSD},${TM}" >> pbs_output_table.txt 

done < ../all_models.txt

```

``` sh
./generate_table.script
```

This file would process the modified RNAalign output files into an informative table stored in "pbs_output_table.txt" with three columns: name, RMSD, TM. The table can then be read into RStudio, which eases further process.


## Reference
* Robin Pearce, Gilbert S. Omenn, Yang Zhang. De Novo RNA Tertiary Structure Prediction at Atomic Resolution using Geometric Potentials from Deep Learning, submitted, 2022
* Sha Gong, Chengxin Zhang, Yang Zhang. RNA-align: quick and accurate alignment of RNA 3D structures based on size-independent TM-scoreRNA. (2019) Bioinformatics, 35: 4459-4461.



