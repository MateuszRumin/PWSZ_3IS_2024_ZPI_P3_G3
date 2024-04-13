import torch
import numpy as np
from typing import List
import time
import laspy

def estimate_normals_torch(inputpc, max_nn):
    from torch_cluster import knn_graph
    knn = knn_graph(inputpc[:, :3], max_nn, loop=False)
    knn = knn.view(2, inputpc.shape[0], max_nn)[0]
    x = inputpc[knn][:, :, :3]
    temp = x[:, :, :3] - x.mean(dim=1)[:, None, :3]
    cov = temp.transpose(1, 2) @ temp / x.shape[0]
    e, v = torch.symeig(cov, eigenvectors=True)
    n = v[:, :, 0]
    return torch.cat([inputpc[:, :3], n], dim=-1)


def estimate_normals(inputpc, max_nn=30, keep_orientation=False):
    try:
        import open3d as o3d
        pcd = o3d.geometry.PointCloud()
        xyz = np.array(inputpc[:, :3].cpu())
        pcd.points = o3d.utility.Vector3dVector(xyz)
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=max_nn))
        normals = np.array(pcd.normals)
        inputpc_unoriented = torch.cat((inputpc[:, :3], torch.Tensor(normals).to(inputpc.device)), dim=1)
        if keep_orientation:
            flip = (inputpc[:, 3:] * inputpc_unoriented[:, 3:]).sum(dim=-1) < 0
            inputpc_unoriented[flip, 3:] *= -1
    except ModuleNotFoundError:
        inputpc_unoriented = estimate_normals_torch(inputpc, max_nn)

    return inputpc_unoriented