import logging
from typing import Dict, List, Type
from abc import ABC, abstractmethod

from rpi_sensorium.infra.measures_storage import MeasuresStorage
from rpi_sensorium.infra import errors


LOGGER = logging.getLogger(__name__)


EXISTING_CONSUMERS = []  # type: List[Type[BaseConsumer]]


class BaseConsumer(ABC):

    # NAME must be unique
    NAME = None  # type: str

    _config = None  # type: Dict
    _storage = None  # type: MeasuresStorage

    def __init__(self, config: Dict, storage: MeasuresStorage):
        if not self.NAME:
            raise errors.ConsumerCreationError(
                f"Can't create an instance of consumer {self}. Class variable NAME isn't defined in this consumer"
            )
        LOGGER.debug("Creating new consumer %s with config %s", self.NAME, config)
        self._config = config
        self._storage = storage

    @abstractmethod
    def initalize(self):
        pass

    @abstractmethod
    def process_measures(self):
        pass

    def __str__(self):
        return f"Consumer: {self.NAME}"

    def __repr__(self):
        return self.__str__()


def register_consumer(consumer: Type[BaseConsumer]):
    EXISTING_CONSUMERS.append(consumer)
