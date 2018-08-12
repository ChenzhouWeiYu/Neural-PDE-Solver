import torch
import torch.nn as nn
import torch.nn.functional as F

from .iterator import Iterator
import utils

class UNetIterator(Iterator):
  def __init__(self, act, nf=1):
    super(UNetIterator, self).__init__(act)

    self.layers = nn.Sequential(
                      nn.Conv2d(1, nf, 4, 2, 0, bias=False),
                      nn.ConvTranspose2d(nf, 1, 4, 2, 1, bias=False)
                  )

  def forward(self, x, bc):
    # Same padding. Conv2d uses zero-pad, which doesn't make sense.
    x_pad = F.pad(x, (1, 1, 1, 1), 'replicate')
    y = x + self.layers(x_pad) # residual
    y = self.activation(y)
    # Set boundary
    inner = y.squeeze(1)[:, 1:-1, 1:-1]
    y = utils.pad_boundary(inner, bc).unsqueeze(1) # same size as x
    return y