from abc import abstractmethod
from typing import Dict

import busio

from rpi_sensorium.sensors import base
from rpi_sensorium.infra import errors


class I2CSensorBase(base.BaseSensor):

    I2C_ADDRESS = None  # type: int

    def __init__(self, config: Dict, i2c: busio.I2C):
        super().__init__(config)
        if self.I2C_ADDRESS is None:
            raise errors.SensorCreationError(
                f"Can't create an instance of I2C sensor {self}. Class"
                f"variable I2C_ADDRESS isn't defined in this sensor"
            )
        self._i2c = i2c

    @abstractmethod
    def initalize(self):
        pass

    def __str__(self):
        return f"I2C Sensor: {self.NAME} with address {self.I2C_ADDRESS}"

    def __repr__(self):
        return self.__str__()
