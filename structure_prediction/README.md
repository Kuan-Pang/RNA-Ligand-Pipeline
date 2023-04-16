# Structure Prediction

This folder includes scripts and instruction on the workflow of predicting structure using DeepFoldRNA, and the downstream evaluation on the predicted models using RNAalign and R language.

This workflow is referenced to [DeepFoldRNA](https://www.biorxiv.org/content/10.1101/2022.05.15.491755v1) and [RNAalign](https://pubmed.ncbi.nlm.nih.gov/31161212/).

## Setup DeepFoldRNA
* Install DeepFoldRNA onto cluster by cloning their [GitHub repo](https://github.com/robpearc/DeepFoldRNA)
* Follow the instructions in the repo to download the required programs and databases

## Setup RNAalign
* Download RNAalign program from [Zhang Lab Website](https://seq2fun.dcmb.med.umich.edu//RNA-align/download.html)

## Predicting RNA structures using DeepFoldRNA
An automatic bash script for submiting jobs in batch to clusters is included in this directory. Note that the input fasta files must be named as seq.fasta for all sequences, and been placed in individual folders, for example, if the riboswitch is named as 2cky, then there should be a folder named 2cky, and only contains a filed named "seq.fasta" within this folder, containing the fasta format sequence of the riboswitch.

``` sh
code
```


## Reference
* Robin Pearce, Gilbert S. Omenn, Yang Zhang. De Novo RNA Tertiary Structure Prediction at Atomic Resolution using Geometric Potentials from Deep Learning, submitted, 2022
* Sha Gong, Chengxin Zhang, Yang Zhang. RNA-align: quick and accurate alignment of RNA 3D structures based on size-independent TM-scoreRNA. (2019) Bioinformatics, 35: 4459-4461.



