import torch
import torch.nn as nn
import torch.nn.functional as F

from .iterator import Iterator
import utils

class ConvIterator(Iterator):
  def __init__(self, act, n_layers=1):
    super(ConvIterator, self).__init__(act)

    layers = []
    for i in range(n_layers):
      layers += [nn.ReplicationPad2d(1),
                 nn.Conv2d(1, 1, 3, stride=1, padding=0, bias=False)]
    self.layers = nn.Sequential(*layers)
    self.n_layers = n_layers

  def forward(self, x, bc):
    '''
    x: size (batch_size x 1 x image_size x image_size)
    return: same size
    '''
    z = F.conv2d(x, self.fd_update_kernel)
    y = x[:, :, 1:-1, 1:-1] - z

    y = self.layers(y)
    y = z + y # residual

    y = self.activation(y)
    # Set boundary
    y = utils.pad_boundary(y.squeeze(1), bc).unsqueeze(1) # same size as x
    return y
