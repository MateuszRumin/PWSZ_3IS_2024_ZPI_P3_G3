import torch
from pathlib import Path
from normalization.transform_data import point_tensor, Transform,tensor_to_pc
from normalization.util import estimate_normals, divide_pc,orient_center
from normalization.interface_utils import load_model_from_file,fix_n_filter,voting_policy
from normalization.field_utils import strongest_field_propagation_reps,measure_mean_potential
modelsPath = ["./normalization/pre_trained/hands2.pt", "./normalization/pre_trained/hands.pt", "./normalization/pre_trained/manmade.pt" ]
torch.manual_seed(1)

def orient_large(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,n):
    max_patch_size = 500
    device = torch.device(torch.cuda.current_device() if torch.cuda.is_available() else torch.device('cpu'))
    print("Transfer do tensor")
    # przerobienie na tens
    input_pc = point_tensor(points).to(device)
    input_pc, transform = Transform.trans(input_pc)
    print("Transfer do tensor- koniec")
    print("Est_norm")
    input_pc = estimate_normals(input_pc, max_nn=n)
    softmax = torch.nn.Softmax(dim=-1)
    models = [load_model_from_file(Path(i), device) for i in modelsPath]
    print("Est_norm_end")
    print("devide patches")
    patch_indices = divide_pc(input_pc[:,:3],number_of_parts,min_patch=min_points_on_path)
    all_patches_indices = [x.clone() for x in patch_indices]
    print("end devide patches")
    print("filter patches")
    patch_indices = fix_n_filter(input_pc, patch_indices,curvature_threshold)
    num_patches = len(patch_indices)
    num_all_patches = len(all_patches_indices)
    print(f'number of patches {num_patches}/{num_all_patches}')
    print("end filter patches")
    print("orient center")
    for i, p in patch_indices:
        input_pc[p] = orient_center(input_pc[p])
    print("end orient center")
    print("find reps")
    represent = []
    for p in all_patches_indices:
        permutation = torch.randperm(p.shape[0])
        represent.append((p[permutation[:max_patch_size]], p[permutation[max_patch_size:]]))

    pc_probs = torch.ones_like(input_pc[:, 0])
    print("end find reps")
    print("net orientation")

    for i, _ in patch_indices:
        with torch.no_grad():
            current_reps, non_reps_points = represent[i]

            data = input_pc[current_reps]

            data = data.to(device)

            for _ in range(model_iterations):
                votes = [model(data.clone()) for model in models]
                vote_probabilities = [softmax(scores)[:, 1] for scores in votes]
                flip, probs = voting_policy(vote_probabilities)
                pc_probs[current_reps] = probs
                input_pc[current_reps[flip], 3:] *= -1

    print("end net orientation")
    [model.to('cpu') for model in models]
    print("propagating field")
    # strongest_field_propagation_reps(input_pc, represent, diffuse=True)
    print("end propagating field")
    print("fix global orientation")
    if measure_mean_potential(input_pc) < 0:
        # if average global potential is negative, flip all normals
        input_pc[:, 3:] *= -1
    print("end fix global orientation")
    print("end transform back to point cloud")
    rtn = tensor_to_pc(input_pc)
    print("end transform back to point cloud")
    return rtn


def orient_normal(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,n):
    device = torch.device(torch.cuda.current_device() if torch.cuda.is_available() else torch.device('cpu'))
    print(device)