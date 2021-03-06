import numpy as np

from .misc import to_numpy

class Metrics(object):
  def __init__(self, scale, error_threshold):
    print('Runtime scaling: {}'.format(scale))
    self.scale = scale
    self.error_threshold = error_threshold
    self.model_steps = []
    self.fd_steps = []
    self.invalid = 0

  def update(self, error_dict):
    errors = to_numpy(error_dict['model errors'])
    if 'Jacobi errors' not in error_dict:
      # No comparision
      fd_errors = errors
    else:
      fd_errors = to_numpy(error_dict['Jacobi errors'])
    batch_size, length = errors.shape
    for i in range(batch_size):
      if np.any(fd_errors[i] < self.error_threshold) and \
         np.any(errors[i] < self.error_threshold):
        model_step = np.nonzero(errors[i] < self.error_threshold)[0][0]
        fd_step = np.nonzero(fd_errors[i] < self.error_threshold)[0][0]
        model_step *= self.scale # scaling for model
        self.model_steps.append(model_step)
        self.fd_steps.append(fd_step)
      else:
        self.invalid += 1

  def get_results(self):
    print('Invalid: {}/{}'.format(self.invalid, len(self.fd_steps) + self.invalid))
    self.model_steps = np.array(self.model_steps)
    self.fd_steps = np.array(self.fd_steps)
    ratios = self.model_steps / self.fd_steps
    results = {'Jacobi': self.fd_steps.mean(),
               'model': self.model_steps.mean(),
               'ratio': ratios.mean()}
    return results

  def reset(self):
    self.model_steps = []
    self.fd_steps = []
    self.invalid = 0
