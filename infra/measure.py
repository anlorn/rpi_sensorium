from typing import Union
from datetime import datetime

from rpi_sensorium.infra.data_types import SupportedDataTypes


class Measure:
    def __init__(self, value: Union[int, float], measured_at: datetime, unit: str, data_type: SupportedDataTypes):
        self._value = value
        self._measured_at = measured_at
        self._unit = unit
        self._data_type = data_type

    @property
    def value(self):
        return self._value

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def data_type(self) -> SupportedDataTypes:
        return self._data_type

    @property
    def measured_at(self):
        return self._measured_at

    def __str__(self):
        return str.format("{value} {unit}", value=self._value, unit=self._unit)

    def __repr__(self):
        return self.__str__()
