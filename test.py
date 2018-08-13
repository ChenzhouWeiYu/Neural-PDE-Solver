import glob
import numpy as np
import os
import torch

import data
import utils
from models.heat_model import HeatModel


def evaluate(opt, model, data_loader, logger, vis=None):
  model.setup(is_train=False)

  # Construct update matrix
  bc = np.random.rand(1, 4)
  A, B = utils.construct_matrix(bc, 16, model.iter_step)
  w, v = np.linalg.eig(B)
  logger.print('Eigenvalues:\n{}\n'.format(w))
  logger.print('Absolute eigenvalues:\n{}\n'.format(sorted(np.abs(w))))

  for step, data in enumerate(data_loader):
    bc, final, x = data['bc'], data['final'], data['x']
    error_dict = model.evaluate(x, final, bc, opt.n_evaluation_steps, opt.switch_to_fd)
    images = utils.plot_error_curves(error_dict)
    if vis is not None:
      vis.add_image({'errors': images}, step)
    if (step + 1) % opt.log_every == 0:
      print('Step {}'.format(step))
    if (step + 1) == 20:
      # Hard code for now
      break

def main():
  opt, logger, stats, vis = utils.build(is_train=False, tb_dir='tb_val')
  # Load model opt
  model_opt = np.load(os.path.join(opt.ckpt_path, 'opt.npy')).item()
  model_opt.is_train = False
  model = HeatModel(model_opt)
  logger.print('Loading data from {}'.format(opt.dset_path))

  # In case I forget
  opt.zero_init = model_opt.zero_init
  data_loader = data.get_data_loader(opt)

  for epoch in opt.which_epochs:
    if epoch < 0:
      # Pick last epoch
      checkpoints = glob.glob(os.path.join(opt.ckpt_path, 'net_*.pth'))
      assert len(checkpoints) > 0
      epochs = [int(path[:-4].split('_')[-1]) for path in checkpoints]
      epoch = sorted(epochs)[-1]

    model.load(opt.ckpt_path, epoch)
    logger.print('Checkpoint loaded from {}, epoch {}'.format(opt.ckpt_path, epoch))
    evaluate(opt, model, data_loader, logger, vis)

if __name__ == '__main__':
  main()
