from typing import Optional

from math import ceil

import torch
from torch import Tensor
from torch.nn import Sequential as S, Linear as L  # , BatchNorm1d as BN
from torch.nn import Identity as Identity
from torch.nn import ELU, Conv1d
from torch_geometric.nn import Reshape

from normalization.models.inits import reset

try:
    from torch_cluster import knn_graph
except ImportError:
    knn_graph = None


class XConv(torch.nn.Module):

    def __init__(self, in_channels: int, out_channels: int, dim: int,
                 kernel_size: int, hidden_channels: Optional[int] = None,
                 dilation: int = 1, bias: bool = True, num_workers: int = 1):
        super(XConv, self).__init__()

        if knn_graph is None:
            raise ImportError('`XConv` requires `torch-cluster`.')

        self.in_channels = in_channels
        if hidden_channels is None:
            hidden_channels = in_channels // 4
        assert hidden_channels > 0
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.dim = dim
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.num_workers = num_workers

        C_in, C_delta, C_out = in_channels, hidden_channels, out_channels
        D, K = dim, kernel_size

        self.mlp1 = S(
            L(dim, C_delta),
            ELU(),
            Identity(),
            L(C_delta, C_delta),
            ELU(),
            Identity(),
            Reshape(-1, K, C_delta),
        )

        self.mlp2 = S(
            L(D * K, K**2),
            ELU(),
            Identity(),
            Reshape(-1, K, K),
            Conv1d(K, K**2, K, groups=K),
            ELU(),
            Identity(),
            Reshape(-1, K, K),
            Conv1d(K, K**2, K, groups=K),
            Identity(),
            Reshape(-1, K, K),
        )

        # C_in = C_in + C_delta
        depth_multiplier = int(ceil(C_out / C_in))
        self.conv = S(
            Conv1d(C_in, C_in * depth_multiplier, K, groups=C_in),
            Reshape(-1, C_in * depth_multiplier),
            L(C_in * depth_multiplier, C_out, bias=bias),
        )

        self.reset_parameters()


    def reset_parameters(self):
        reset(self.mlp1)
        reset(self.mlp2)
        reset(self.conv)

    def forward(self, x: Tensor, pos: Tensor, batch: Optional[Tensor] = None):
        """"""
        pos = pos.unsqueeze(-1) if pos.dim() == 1 else pos
        (N, D), K = pos.size(), self.kernel_size

        edge_index = knn_graph(pos, K * self.dilation, batch, loop=True,
                               flow='target_to_source',
                               num_workers=self.num_workers)
        row, col = edge_index[0], edge_index[1]

        if self.dilation > 1:
            dil = self.dilation
            index = torch.randint(K * dil, (N, K), dtype=torch.long,
                                  device=row.device)
            arange = torch.arange(N, dtype=torch.long, device=row.device)
            arange = arange * (K * dil)
            index = (index + arange.view(-1, 1)).view(-1)
            row, col = row[index], col[index]

        pos = pos[col] - pos[row]

        if x is not None:
            x = x.unsqueeze(-1) if x.dim() == 1 else x
            x_knn = x[col].view(N, K, self.in_channels)
        else:
            x_knn = self.mlp1(pos.view(N * K, D))

        x_star = x_knn
        x_star = x_star.transpose(1, 2).contiguous()
        x_star = x_star.view(N, self.in_channels, K, 1)
        transform_matrix = self.mlp2(pos.view(N, K * D))
        transform_matrix = transform_matrix.view(N, 1, K, K)

        x_transformed = torch.matmul(transform_matrix, x_star)
        x_transformed = x_transformed.view(N, -1, K)

        out = self.conv(x_transformed)

        return out

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.in_channels,
                                   self.out_channels)