import logging
from typing import Union


from rpi_sensorium.infra.data_types import SupportedDataTypes
from rpi_sensorium.infra.measure import Measure
from rpi_sensorium.infra import errors

LOGGER = logging.getLogger(__name__)


class MeasuresStorage:

    def __init__(self):
        self.measures = {}
        for supported_data_type in SupportedDataTypes:
            self.measures[supported_data_type] = []

    def add_measure(self, measure: Measure):
        """
        Add a new measure to a storage
        """
        LOGGER.debug("Trying to add a measure %s of type %s", measure, measure.data_type)
        if measure.data_type not in self.measures:
            raise errors.UnknownDataType(
                f"Can't add a measure {measure} with data type {measure.data_type}. Unknown data type."
            )
        self.measures[measure.data_type].append(measure)
        self.measures[measure.data_type].sort(key=lambda x: x.measured_at)
        LOGGER.debug(
            "Storage for measures of type %s, now has %d records",
            measure,
            len(self.measures[measure.data_type])
        )

    def get_last_measure_by_data_type(self, data_type: SupportedDataTypes) -> Union[Measure, None]:
        """
        Retrieve the latest measure of a specific type from the storage. Return None of storage has
        no measures of this type
        """
        if data_type not in SupportedDataTypes:
            raise errors.UnknownDataType(f"Can't get measure with data type {data_type}, because data type is unknown")
        if not self.measures[data_type]:
            return None
        LOGGER.debug(
            "Returning last measure of type %s, total number of stored measures %d",
            data_type,
            len(self.measures[data_type])
        )
        return self.measures[data_type][-1]
