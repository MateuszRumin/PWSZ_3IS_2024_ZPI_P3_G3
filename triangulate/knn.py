import torch
#import igl
import numpy as np
import sklearn.neighbors

from triangulate import world
from triangulate import utils
from triangulate.utils import *

import torch_cluster 


def find_knn(points_source, points_target, k, largest=False, omit_diagonal=False, method='brute', prebuilt_tree=None):

    if omit_diagonal and points_source.shape[0] != points_target.shape[0]:
        raise ValueError("omit_diagonal can only be used when source and target are same shape")

    if method != 'cpu_kd' and points_source.shape[0] * points_target.shape[0] > 1e8:
        method = 'cpu_kd'
        print("switching to cpu_kd knn")

    if method == 'brute':

        # Expand so both are NxMx3 tensor
        points_source_expand = points_source.unsqueeze(1)
        points_source_expand = points_source_expand.expand(-1, points_target.shape[0], -1)
        points_target_expand = points_target.unsqueeze(0)
        points_target_expand = points_target_expand.expand(points_source.shape[0], -1, -1)

        diff_mat = points_source_expand - points_target_expand
        dist_mat = norm(diff_mat)

        if omit_diagonal:
            torch.diagonal(dist_mat)[:] = float('inf')

        result = torch.topk(dist_mat, k=k, largest=largest, sorted=True)
        return result
    
    elif method == 'cpu_kd':

        if largest:
            raise ValueError("can't do largest with cpu_kd")

        points_source_np = toNP(points_source)

        # Build the tree
        if prebuilt_tree is not None:
            kd_tree = prebuilt_tree
        else:
            points_target_np = toNP(points_target)
            kd_tree = sklearn.neighbors.KDTree(points_target_np)

        k_search = k+1 if omit_diagonal else k 
        _, neighbors = kd_tree.query(points_source_np, k=k_search)
        
        if omit_diagonal: 
            # Mask out self element
            mask = neighbors != np.arange(neighbors.shape[0])[:, np.newaxis]

            # make sure we mask out exactly one element in each row, in rare case of many duplicate points
            mask[np.sum(mask, axis=1) == mask.shape[1], -1] = False

            neighbors = neighbors[mask].reshape((neighbors.shape[0], neighbors.shape[1]-1))

        inds = torch.tensor(neighbors, device=points_source.device, dtype=torch.int64)
        dists = norm(points_source.unsqueeze(1).expand(-1, k, -1) - points_target[inds])

        return dists, inds

    else:
        raise ValueError("unrecognized method")






