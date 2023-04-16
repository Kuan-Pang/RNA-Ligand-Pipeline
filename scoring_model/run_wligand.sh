#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=test_run
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=0-11:30

case_name="equiformer_ligand"

module load python/3.8


cd $SLURM_TMPDIR
tar -xzf selected_sample.tar.gz
echo "rna samples extracted"
tar -xzf rna_ligand_samples.tar.gz
echo "rna-ligand samples extracted"

echo "tmp_dir" $SLURM_TMPDIR

log_dir=${case_name}
mkdir -p ${log_dir}
echo "log_dir" $log_dir


echo "initing python"


srun python test_run_wligand.py $SLURM_TMPDIR $log_dir