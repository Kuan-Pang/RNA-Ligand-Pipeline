#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --cpus-per-task=8
#SBATCH --array=1-354
#SBATCH --mem=32G

echo "starting"

module load nixpkgs/16.09  gcc/7.3.0
module load openbabel/2.4.1

# SLURM_ARRAY_TASK_ID=1
rna_name=$(sed -n "${SLURM_ARRAY_TASK_ID}p" case_list)
echo "Starting task ${SLURM_ARRAY_TASK_ID} : ${rna_name}"


./dock_ligand.sh ${rna_name}
status=$?
[ $status -eq 0 ] && echo "command successful" || echo $rna_name "${SLURM_ARRAY_TASK_ID}p" >> unsuccessful.out