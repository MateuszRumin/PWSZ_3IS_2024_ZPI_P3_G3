import torch
from pathlib import Path
from normalization.transform_data import point_tensor, Transform
from normalization.util import estimate_normals
from normalization.interface_utils import load_model_from_file

modelsPath = ["./normalization/pre_trained/hands2.pt", "./normalization/pre_trained/hands.pt", "./normalization/pre_trained/manmade.pt" ]


def orient_large(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,n):
    max_patch_size = 500
    device = torch.device(torch.cuda.current_device() if torch.cuda.is_available() else torch.device('cpu'))
    print("Transfer do tensor")
    # przerobienie na tens
    input_pc = point_tensor(points).to(device)
    input_pc, transform = Transform.trans(input_pc)
    print("Transfer do tensor- koniec")
    print("Est_norm")
    input_pc = estimate_normals(input_pc,max_nn=n)
    softmax = torch.nn.Softmax(dim=1)
    models = [load_model_from_file(Path(i), device) for i in modelsPath]
    print("Est_norm_end")





def orient_normal(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,n):
    device = torch.device(torch.cuda.current_device() if torch.cuda.is_available() else torch.device('cpu'))
    print(device)