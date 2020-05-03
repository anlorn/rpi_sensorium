import sys
import time
import logging
from typing import List, Type


from rpi_sensorium.infra import errors
from rpi_sensorium.sensors.i2c import I2CSensorBase
from rpi_sensorium.infra.measures_storage import MeasuresStorage
from rpi_sensorium.sensors.base import BaseSensor, AVAILABLE_SENSORS
from rpi_sensorium.consumers.base import BaseConsumer, EXISTING_CONSUMERS

LOGGER = logging.getLogger(__name__)


def detect_connected_i2c_sensors() -> List[Type[I2CSensorBase]]:
    return AVAILABLE_SENSORS  # TODO: Add actual I2C bus scanning, and using only i2c sensors


def initialize_sensors() -> List[BaseSensor]:
    active_sensors = []  # type: List[BaseSensor]
    available_i2c_sensors = detect_connected_i2c_sensors()
    LOGGER.info("Found %d I2C sensors", len(available_i2c_sensors))

    for available_i2c_sensor in available_i2c_sensors:
        LOGGER.debug("Will try to create sensor %s", available_i2c_sensor)
        try:
            created_sensor = available_i2c_sensor({})  # TODO: config from yaml
            active_sensors.append(created_sensor)
            LOGGER.debug("Initalized sensors %s", created_sensor)
        except errors.SensorError as exc:
            LOGGER.error("Can't initalize %s, err '%s', will skip this sensor", created_sensor, exc)
    return active_sensors


def initialize_consumers(storage: MeasuresStorage) -> List[BaseConsumer]:
    active_consumers = []  # type: List[BaseConsumer]
    for consumer in EXISTING_CONSUMERS:
        LOGGER.debug("Will try to create consumer %s", consumer)
        created_consumer = consumer({}, storage)  # TODO: config from yaml
        try:
            created_consumer.initalize()
            active_consumers.append(created_consumer)
            LOGGER.debug("Initalized consumer %s", created_consumer)
        except errors.ConsumerError as exc:
            LOGGER.error("Can't initalize %s, err '%s', will skip this consumer", created_consumer, exc)
    return active_consumers


def main():
    storage = MeasuresStorage()
    LOGGER.info("Initalized storage")

    active_sensors = initialize_sensors()
    if not active_sensors:
        LOGGER.error("No active sensors were found, exiting...")
        sys.exit(1)
    LOGGER.info("Initalized %d sensors", len(active_sensors))

    active_consumers = initialize_consumers(storage)

    if not active_consumers:
        LOGGER.error("No active consumers were found, exiting...")
        sys.exit(2)

    LOGGER.info("Initalized %d consumers", len(active_consumers))

    main_loop(storage, active_sensors, active_consumers)
    sys.exit(0)  # TODO add signal handler


def main_loop(storage: MeasuresStorage, sensors: List[BaseSensor], consumers: List[BaseConsumer]):
    LOGGER.info("Starting main loop")
    while True:
        time.sleep(1)  # TODO: think about asyncio
        for sensor in sensors:
            LOGGER.debug("Will try to get measure from %s", sensor)
            measure = sensor.get_measure()
            LOGGER.debug("Will try to save measure %s from %s", measure, sensor)
            try:
                storage.add_measure(measure)
            except errors.UnknownDataType as exc:
                LOGGER.warning("Can't add Measure %s from %s. Err: %s", measure, sensor, exc)
            time.sleep(0.5)
        for consumer in consumers:
            LOGGER.debug("Will try to process measures on %s", consumer)
            consumer.process_measures()


if __name__ == '__main__':
    # TODO rewrite to argparse
    if len(sys.argv) >= 2 and sys.argv[1].lower() == 'debug':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    main()
