import torch
from pathlib import Path
from collections import namedtuple
from normalization.models.pointcnn import PointCNN

def txt2opts(path: Path):
    attr = ['pool']
    opts_dict = {}
    opts = open(path, 'r').read()
    for line in opts.split('\n'):
        line = line.replace(' ', '')
        tokens = line.split(':')
        if tokens[0] in attr:
            if tokens[0] == 'pool':
                val = float(tokens[1])
            else:
                val = tokens[1]

            opts_dict[tokens[0]] = val

    Opts = namedtuple('Opts', opts_dict)
    return Opts(**opts_dict)


def load_model_from_file(file: Path, device):
    opts_file = file.with_suffix('.txt')
    model_opts = txt2opts(opts_file)
    model = PointCNN(model_opts, 6, 16).to(device)
    model.load_state_dict(torch.load(file))
    model.eval()
    return model