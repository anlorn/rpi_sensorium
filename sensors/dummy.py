import logging
from typing import List
from random import random
from datetime import datetime

from rpi_sensorium.sensors.base import register_sensor
from rpi_sensorium.sensors.i2c import I2CSensorBase
from rpi_sensorium.infra import data_types, measure

LOGGER = logging.getLogger(__name__)


class DummyI2CSensor(I2CSensorBase):

    NAME = "dummy"
    I2C_ADDRESS = 0x00

    def initalize(self):
        LOGGER.info("Initializing sensor %s", self.NAME)

    def adjust(self, measures: List[measure.Measure]):
        LOGGER.info("Adjusting sensor %s with measures %s", self.NAME, measures)

    def get_measure(self) -> measure.Measure:
        dummy_measure = measure.Measure(
            value=random() * 2000,
            measured_at=datetime.now(),
            unit='hpa',
            data_type=data_types.SupportedDataTypes.PRESSURE
        )
        return dummy_measure


register_sensor(DummyI2CSensor)
