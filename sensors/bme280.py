from datetime import datetime
from typing import List

import adafruit_bme280

from rpi_sensorium.sensors import i2c, base
from rpi_sensorium.infra.measure import Measure
from rpi_sensorium.infra.data_types import SupportedDataTypes


class BME280Sensor(i2c.I2CSensorBase):

    NAME = 'bme280'
    I2C_ADDRESS = 0x76  # TODO think how to handle more than one addres per sensor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bme280 = adafruit_bme280.Adafruit_BME280_I2C(self._i2c, address=self.I2C_ADDRESS)

    def initalize(self):
        pass

    def get_measures(self) -> List[Measure]:
        temperature = Measure(
            self._bme280.temperature,
            datetime.now(),
            'C',
            SupportedDataTypes.TEMPERATURE
        )
        pressure = Measure(
            self._bme280.pressure,
            datetime.now(),
            'hPa',
            SupportedDataTypes.PRESSURE
        )
        humidity = Measure(
            self._bme280.humidity,
            datetime.now(),
            '%',
            SupportedDataTypes.HUMIDITY
        )
        return [temperature, pressure, humidity]

    def adjust(self, measures: List[Measure]):
        pass


base.register_sensor(BME280Sensor)
