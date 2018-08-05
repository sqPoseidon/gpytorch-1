from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import torch
from torch.nn import ModuleList
from copy import deepcopy
from gpytorch.means import Mean


class MultitaskMean(Mean):
    """
    Convenience :class:`gpytorch.means.Mean` implementation for defining a different mean for each task in a multitask
    model. Expects a list of `n_tasks` different mean functions, each of which is applied to the given data in
    :func:`~gpytorch.means.MultitaskMean.forward` and returned as an `n x t` matrix of means, one for each task.
    """
    def __init__(self, base_means, n_tasks):
        """
        Args:
            base_means (:obj:`list` or :obj:`gpytorch.means.Mean`): If a list, each mean is applied to the data.
                If a single mean (or a list containing a single mean), that mean is copied `t` times.
            n_tasks (int): Number of tasks. If base_means is a list, this should equal its length.
        """
        super(MultitaskMean, self).__init__()

        if isinstance(base_means, Mean):
            base_means = [base_means]

        if not isinstance(base_means, list) or (len(base_means) != 1 and len(base_means) != n_tasks):
            raise RuntimeError("base_means should be a list of means of length either 1 or n_tasks")

        if len(base_means) == 1:
            base_means = base_means + deepcopy([base_means[i] for i in range(n_tasks - 1)])

        self.base_means = ModuleList(base_means)
        self.n_tasks = n_tasks

    def forward(self, input):
        """
        Evaluate each mean in self.base_means on the input data, and return as an `n x t` matrix of means.
        """
        return torch.cat([sub_mean(input).unsqueeze(-1) for sub_mean in self.base_means], dim=-1)
