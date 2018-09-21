import glob
import numpy as np
import os
import time
import torch

import data
import utils
from models.heat_model import HeatModel

def runtime(opt, model, data_loader):
  '''
  Test runtime.
  '''
  for step, data in enumerate(data_loader):
    bc, gt, x = data['bc'], data['final'], data['x']
    bc = bc.cuda()
    gt = gt.cuda()
    x = x.cuda()
    # Initialize with zeros and calculate starting_error
    x = utils.initialize(x, bc, 'zero')
    starting_error = utils.l2_error(x, gt).cpu()

    # Initialize
    x = utils.initialize(x, bc, opt.initialization)
    # Get the errors first
    threshold = 0.001
    errors, _ = utils.calculate_errors(x, bc, None, gt, model.iter_step,
                                       opt.n_evaluation_steps, starting_error,
                                       threshold)
    errors = errors[0].cpu().numpy()

    steps = np.nonzero(errors < threshold)[0][0]
    print('Steps:', steps)

    # Measure time
    start_t = time.time()
    for i in range(steps):
      y = model.iter_step(x, bc, None).detach()
    end_t = time.time()
    t = end_t - start_t
    print('Time: {}'.format(t))

def main():
  opt, logger, stats, vis = utils.build(is_train=False, tb_dir=None, logging=None)
  assert opt.geometry == 'square'
  # Load model opt
  model_opt = np.load(os.path.join(opt.ckpt_path, 'opt.npy')).item()
  model_opt.is_train = False
  # Change geometry to the testing one
  model_opt.geometry = opt.geometry
  model = HeatModel(model_opt)
  print('Loading data from {}'.format(opt.dset_path))

  # For convenience
  opt.iterator = model_opt.iterator

  opt.initialization = 'avg'
  opt.data_limit = 1
  opt.batch_size = 1
  data_loader = data.get_data_loader(opt)

  epoch = opt.which_epochs[0]
  if epoch < 0:
    # Pick last epoch
    checkpoints = glob.glob(os.path.join(opt.ckpt_path, 'net_*.pth'))
    assert len(checkpoints) > 0
    epochs = [int(path[:-4].split('_')[-1]) for path in checkpoints]
    epoch = sorted(epochs)[-1]

  model.load(opt.ckpt_path, epoch)
  print('Checkpoint loaded from {}, epoch {}'.format(opt.ckpt_path, epoch))
  model.setup(is_train=False)
  runtime(opt, model, data_loader)

if __name__ == '__main__':
  main()
