import sys
import time
import logging
from typing import List, Type

import busio
import board

from rpi_sensorium.infra import errors
from rpi_sensorium.sensors.i2c import I2CSensorBase
from rpi_sensorium.infra.measures_storage import MeasuresStorage
from rpi_sensorium.sensors.base import BaseSensor, AVAILABLE_SENSORS
from rpi_sensorium.consumers.base import BaseConsumer, EXISTING_CONSUMERS

LOGGER = logging.getLogger(__name__)


def detect_connected_i2c_sensors(i2c_bus: busio.I2C) -> List[Type[I2CSensorBase]]:
    connected_i2c_sensors = []  # type: List[Type[I2CSensorBase]]
    found_i2c_addresses = set(i2c_bus.scan())
    LOGGER.debug("Found following i2c devices addresses: %s", found_i2c_addresses)
    for sensor_cls in AVAILABLE_SENSORS:
        if issubclass(sensor_cls, (I2CSensorBase,)):
            if sensor_cls.I2C_ADDRESS in found_i2c_addresses:
                LOGGER.info(
                    "Sensor %s with address %s is connected to I2C bus, will use this sensor",
                    sensor_cls,
                    sensor_cls.I2C_ADDRESS,
                )
                connected_i2c_sensors.append(sensor_cls)
            else:
                LOGGER.debug(
                    "Sensor class '%s' has I2C address %s which isn't found on i2c bus, skipping sensor",
                    sensor_cls,
                    sensor_cls.I2C_ADDRESS
                )
        else:
            LOGGER.debug("Sensor class %s isn't an I2C sensor, skip it", sensor_cls)
    return connected_i2c_sensors


def initialize_sensors() -> List[BaseSensor]:
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    LOGGER.info("Initalized I2C bus")
    active_sensors = []  # type: List[BaseSensor]
    available_i2c_sensors = detect_connected_i2c_sensors(i2c_bus)
    LOGGER.info("Found %d I2C sensors", len(available_i2c_sensors))

    for available_i2c_sensor in available_i2c_sensors:
        LOGGER.debug("Will try to create sensor %s", available_i2c_sensor)
        try:
            created_sensor = available_i2c_sensor({}, i2c_bus)  # TODO: config from yaml
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
            LOGGER.debug("Will try to get measures from %s", sensor)
            sensor.adjust([])  # TODO add actual measures list
            measures = sensor.get_measures()
            for measure in measures:
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
