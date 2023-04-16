entry_name=$1

MOL2_FILE_DIR=""
DOCK_FILE_DIR=""


echo $entry_name
mol2_entry_dir=${MOL2_FILE_DIR}/${entry_name}
dock_entry_dir=${DOCK_FILE_DIR}/${entry_name}
mkdir -p ${dock_entry_dir}
total_ligand=`find ${mol2_entry_dir} | wc -l`
total_ligand=$( expr $total_ligand - 2 )
curr_rna_path=${mol2_entry_dir}/${entry_name}_rna.mol2
# echo $curr_rna_path

for k in $(seq 1 $total_ligand); do
    curr_ligand=$( expr $k - 1 )
    curr_ligand_path=${mol2_entry_dir}/${entry_name}_ligand_${curr_ligand}.mol2
    # echo $curr_ligand_path
    entry_prefix=${dock_entry_dir}/${entry_name}_${curr_ligand}
        ./RLDOCK/RLDOCK -i ${curr_rna_path} -l ${curr_ligand_path} -o ${entry_prefix} -c 10 -n 4 \
    -s ./RLDOCK/src/sphere.dat

    mol_file_path=${entry_prefix}_cluster.mol2
    pdb_file_path=${entry_prefix}.pdb

    babel -imol2 ${mol_file_path} -opdb $pdb_file_path
done

rm ${dock_entry_dir}/*.mol2
rm ${dock_entry_dir}/*.dat
rm ${dock_entry_dir}/*.xyz

