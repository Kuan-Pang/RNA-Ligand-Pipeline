# %%
from equiformer_pytorch import Equiformer
from data import PDB_DATASET, load_case_list
import torch
from equiformer_pytorch import Equiformer
from torch.utils.data import DataLoader
from torch import nn
import tqdm
import os
import numpy as np
import sys

# %%
slurm_tmp = sys.argv[1]
save_dir = sys.argv[2]
EPOCH = 30
# EPOCH = 8
print(f"starting..., running {EPOCH} epoches")
# %%
# path
selected_train_list_path = ""
selected_eval_list_path = ""

ligand_train_list_path = ""
ligand_eval_list_path = ""
selected_path = os.path.join(slurm_tmp, "selected_sample")
ligand_path = os.path.join(slurm_tmp, "rna_ligand_samples")


# %%
# load case list
selected_train_case_list = load_case_list(selected_train_list_path)
selected_eval_case_list = load_case_list(selected_eval_list_path)
ligand_train_case_list = load_case_list(ligand_train_list_path)
ligand_eval_case_list = load_case_list(ligand_eval_list_path)

# %%
train_dataset = PDB_DATASET([selected_path, ligand_path], [selected_train_case_list, ligand_train_case_list])
# train_dataset = PDB_DATASET([ligand_path], [ligand_train_case_list])
eval_dataset = PDB_DATASET([selected_path, ligand_path], [selected_eval_case_list, ligand_eval_case_list])
train_dataloader = DataLoader(train_dataset, batch_size=1, shuffle=True)
test_dataloader = DataLoader(eval_dataset, batch_size=1, shuffle=True)

# %%
class RMS_predictor(nn.Module):
    def __init__(self):
        super(RMS_predictor, self).__init__()
        self.model = Equiformer(
            num_tokens = train_dataset.element_num,
            dim = (16, 8, 8),               # dimensions per type, ascending, length must match number of degrees (num_degrees)
            dim_head = (16, 8, 8),          # dimension per attention head
            heads = (1, 1, 1),             # number of attention heads
            num_degrees = 3,               # number of degrees
            depth = 3,                     # depth of equivariant transformer
            attend_self = True,            # attending to self or not
            reduce_dim_out = False,         # whether to reduce out to dimension of 1, say for predicting new coordinates for type 1 features
            dot_product_attention = True,  # set to False to try out MLP attention
            num_neighbors = 42
        )
        self.mlp_1 = nn.Linear(16, 256)
        self.relu = nn.ReLU()
        self.mlp_2 = nn.Linear(256, 1)
        
        
    def forward(self, feature, coord, mask=None):
        x = self.model(feature, coord, mask).type0
        x = torch.mean(x, dim=1)
        x = self.mlp_1(x)
        x = self.relu(x)
        x = self.mlp_2(x)
        
        # print(x.shape)
        return x

# %%
loss_fn = torch.nn.MSELoss()
learning_rate = 1e-4

# %%
def train(model, train_loader, loss_fn, learning_rate, num_epochs, grad_accum=16):
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    grad_count = 0
    for epoch in range(num_epochs):
        for sample in train_loader:
            grad_count += 1
            atom_number = sample["num_atom"]
            coord = sample["cord"].cuda()
            feature = sample["ele"].cuda()
            rms = sample["rms"].float().cuda()
            
            try:
                out = model(feature, coord)
                loss = loss_fn(out, rms)
                (loss / grad_accum).backward()
            except:
                print(sample["path"])
            
            
            if grad_count >= 16:
                optimizer.step()
                optimizer.zero_grad()
                grad_count = 0
              
        torch.save(model.state_dict(), os.path.join(save_dir, 'weights.pth'))
        print(f"epoch {epoch}, finished; weights saved")

# %%
def validate(model, test_loader, loss_fn):
    print("validating...")
    pred_array = np.zeros((len(test_loader), 2))
    count = 0
    with torch.no_grad():
        for sample in test_loader:
            atom_number = sample["num_atom"]
            coord = sample["cord"].cuda()
            feature = sample["ele"].cuda()
            rms = sample["rms"].float().cuda()

            out = model(feature, coord)

            pred = out.item()
            gt = rms.item()
            
            pred_array[count][0] = pred
            pred_array[count][1] = gt
            
            count  += 1
            
    return pred_array

# %%
model = RMS_predictor().cuda()
train(model, train_dataloader, loss_fn, learning_rate, EPOCH)

# %%
array = validate(model, test_dataloader, loss_fn)


# %%

np.save(os.path.join(save_dir, 'test_cc.npy'), array)

