import contextlib

import torch

from leaspy.io.data.dataset import Dataset
from leaspy.models.abstract_model import AbstractModel


class AlgoWithDeviceMixin:
    """
    Mixin class containing common attributes & methods for algorithms with a torch device.

    Parameters
    ----------
    settings : :class:`.AlgorithmSettings`
        The specifications of the algorithm as a :class:`.AlgorithmSettings` instance.

    Attributes
    ----------
    algorithm_device : str
        Valid torch device (only the `type` of the device is used)
    """

    def __init__(self, settings):

        super().__init__(settings)

        self.algorithm_device = settings.device

        self._default_algorithm_device = torch.device('cpu')
        # self._default_algorithm_tensor_type = 'torch.FloatTensor'
        self._default_algorithm_tensor_type = torch.float32

    @contextlib.contextmanager
    def _device_manager(self, model: AbstractModel, dataset: Dataset):
        """
        Context-manager to handle the "ambient device" (i.e. the device used
        to instantiate tensors and perform computations). The provided model
        and dataset will be moved to the device specified for the execution
        at the beginning of the algorithm and moved back to the original
        ('cpu') device at the end of the algorithm. The default tensor type
        will also be set accordingly.

        Parameters
        ----------
        model : :class:`~.models.abstract_model.AbstractModel`
            The used model.
        dataset : :class:`.Dataset`
            Contains the subjects' observations in torch format to speed up computation.
        """
        algorithm_tensor_type = self._default_algorithm_tensor_type
        if self.algorithm_device != self._default_algorithm_device.type:
            algorithm_device = torch.device(self.algorithm_device)

            model.move_to_device(algorithm_device)
            dataset.move_to_device(algorithm_device)

            # algorithm_tensor_type = 'torch.cuda.FloatTensor'
            algorithm_tensor_type = torch.cuda.float32

        try:
            # yield torch.set_default_tensor_type(algorithm_tensor_type)
            yield torch.set_default_dtype(algorithm_tensor_type)

        finally:
            if self.algorithm_device != self._default_algorithm_device.type:
                model.move_to_device(self._default_algorithm_device)
                dataset.move_to_device(self._default_algorithm_device)

            # torch.set_default_tensor_type(self._default_algorithm_tensor_type)
            torch.set_default_dtype(algorithm_tensor_type)
