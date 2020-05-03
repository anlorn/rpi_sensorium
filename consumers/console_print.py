import logging
from datetime import datetime

from rpi_sensorium.consumers import base
from rpi_sensorium.infra.data_types import SupportedDataTypes

LOGGER = logging.getLogger(__name__)


class ConsolePrintConsumer(base.BaseConsumer):

    NAME = "console_print"

    def initalize(self):
        pass

    def process_measures(self):
        LOGGER.info("Reading measures of all possible data type at %s", datetime.now())
        for data_type in SupportedDataTypes:
            last_measure = self._storage.get_last_measure_by_data_type(data_type)
            if last_measure is None:
                LOGGER.debug("No measures for %s data type", data_type)
            else:
                LOGGER.info(
                    "Measured At: %s. Value: %s. Data type: %s",
                    last_measure.measured_at, last_measure, data_type
                )


base.register_consumer(ConsolePrintConsumer)
