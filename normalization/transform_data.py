import torch
import numpy as np
from typing import List
import time
import laspy

def point_tensor(points):

    pts = [torch.tensor([x, y, z], dtype=torch.float) for x, y, z in points[:3]]

    rtn = torch.stack(pts, dim=0)
    return rtn



class Transform:
    def __init__(self, pc: torch.Tensor, ttype='reg'):
        if ttype == 'reg':
            self.center = pc[:, :3].mean(dim=0)
            self.scale = (pc[:, :3].max(dim=0)[0] - pc[:, :3].min(dim=0)[0]).max()
        elif ttype == 'bb':
            self.center = pc[:, :3].mean(dim=0)
            pc_tag = pc[:, :3] - self.center
            d = pc[:, :3].sum(dim=-1)
            a, b = d.argmin(), d.argmax()
            line = pc_tag[b] - pc_tag[a]
            self.scale = line.norm()
            mid_points = (pc_tag[a] + pc_tag[b]) / 2
            self.center += mid_points

    def apply(self, pc: torch.Tensor) -> torch.Tensor:
        pc = pc.clone()
        pc[:, :3] -= self.center[None, :]
        pc[:, :3] = pc[:, :3] / self.scale
        return pc

    def inverse(self, pc: torch.Tensor) -> torch.Tensor:
        pc = pc.clone()
        pc[:, :3] = pc[:, :3] * self.scale
        pc[:, :3] += self.center[None, :]
        return pc

    @staticmethod
    def trans(pc: torch.Tensor, ttype='reg'):
        T = Transform(pc, ttype=ttype)
        return T.apply(pc), T