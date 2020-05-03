from enum import Enum


class SupportedDataTypes(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"
    CO2 = "co2"
    TVOC = "tvoc"
