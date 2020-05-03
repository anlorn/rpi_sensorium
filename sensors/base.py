import logging
from typing import Dict, Type, List
from abc import ABC, abstractmethod

from rpi_sensorium.infra import errors
from rpi_sensorium.infra.measure import Measure

LOGGER = logging.getLogger(__name__)


AVAILABLE_SENSORS = []  # type: List[Type[BaseSensor]]


class BaseSensor(ABC):

    NAME = None  # type: str

    def __init__(self, config: Dict):
        if not self.NAME:
            raise errors.SensorCreationError(
                f"Can't create an instance of sensor {self}. Class variable NAME isn't defined in this sensor"
            )
        LOGGER.debug("Creating new sensor %s with config %s", self.NAME, config)
        self._config = config

    @abstractmethod
    def initalize(self):
        pass

    @abstractmethod
    def get_measures(self) -> List[Measure]:
        pass

    @abstractmethod
    def adjust(self, measures: List[Measure]):
        pass

    def __str__(self):
        return f"Sensor: {self.NAME}"

    def __repr__(self):
        return self.__str__()


def register_sensor(sensor: Type[BaseSensor]):
    AVAILABLE_SENSORS.append(sensor)
