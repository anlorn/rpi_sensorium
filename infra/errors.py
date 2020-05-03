class UnknownDataType(Exception):
    pass


class ConsumerError(Exception):
    pass


class ConsumerCreationError(ConsumerError):
    pass


class SensorError(Exception):
    pass


class SensorCreationError(SensorError):
    pass


class NoSensorsFound(Exception):
    pass


class NoConsumersFound(Exception):
    pass
