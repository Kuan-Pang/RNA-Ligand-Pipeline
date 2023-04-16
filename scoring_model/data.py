import os
import numpy as np
from torch.utils.data import Dataset
import glob
from typing import List

import torch

def load_case_list(case_list_path):
    with open(case_list_path, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

class PDB_DATASET(Dataset):
    def __init__(self, file_path_list: List[str], 
                 case_collection_list: List[List[str]], 
                 elemnet_list: List[str] = ['N', 'O', 'P', 'C', 'S', 'F', 'CL', 'BR'],
                 pre_proc=True) -> None:
        super().__init__()
        self.sample_path_list = []
        self.elements = elemnet_list
        self.element_map = {e: i for i, e in enumerate(self.elements)}
        self.element_num = len(self.elements)
        for i in range(len(file_path_list)):
            file_path = file_path_list[i]
            case_collection = case_collection_list[i]
            assert os.path.exists(file_path), f"File {file_path} does not exist"
            for dir_path in glob.glob(file_path + "/*/", recursive = True):
                case_name = os.path.basename(os.path.normpath(dir_path))
                # print (case_name)
                if case_name in case_collection:
                    self.sample_path_list.extend([f for f in glob.glob(dir_path + "/*.pdb")])
        if pre_proc:
            self.sample_list = []
            for sample_path in self.sample_path_list:
                self.sample_list.append(self.parse_pdb(sample_path))
        print(f"Loaded {len(self.sample_list)} samples")
        
    def __len__(self):
        return len(self.sample_path_list)
    
    def __getitem__(self, idx):
        return self.sample_list[idx]

    def parse_pdb(self, pdb_path):
        with open(pdb_path, 'r') as f:
            lines = f.readlines()
        coord = []
        ele = []
        score = None
        atom_count = 0
        for line in lines:
            if line[:4] == 'ATOM' or line[:6] == "HETATM":
                atom_ele = line[76:78].strip().upper()
                if atom_ele != 'H' and atom_ele != 'Z': # exlude hydrogen and dummy atoms
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    atom_coord = torch.tensor([x, y, z])
                    ele.append(self._map_ele(atom_ele))
                    coord.append(atom_coord)
                    atom_count += 1
            if line[:4] == 'rms ':  # not rms_stem
                score = torch.tensor(float(line[4:].strip()))
        coord = torch.stack(coord)
        ele = torch.tensor(ele)
        if score is None:
            raise ValueError("No score found in pdb file")
        return {"cord": coord, "ele": ele, "path": pdb_path, "rms": score,
                "num_atom": atom_count}
    
    # def _map_ele(self, ele):
    #     res = np.zeros((self.element_num))
    #     res[self.element_map[ele]] = 1
    #     return res
    
    def _map_ele(self, ele):
        return self.element_map[ele]
