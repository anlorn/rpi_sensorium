import logging
import time
from datetime import datetime, timedelta
from typing import Union, List

import adafruit_ccs811

from rpi_sensorium.sensors import i2c, base
from rpi_sensorium.infra.measure import Measure
from rpi_sensorium.infra.data_types import SupportedDataTypes

LOGGER = logging.getLogger(__name__)

BASELINE_FILE = "/tmp/ccs811_baseline"


class CCS811Sensor(i2c.I2CSensorBase):
    NAME = 'ccs811'
    I2C_ADDRESS = 0x5a

    PAUSE_BEFORE_READING = timedelta(minutes=20)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ccs811 = adafruit_ccs811.CCS811(self._i2c)
        self.starting_time = datetime.now()
        self.baseline_was_set_after_start = False

    def initalize(self):
        LOGGER.debug("Resetting %s", self.NAME)
        self._ccs811.reset()
        time.sleep(0.5)
        LOGGER.debug("Initializing %s", self.NAME)
        self._ccs811 = adafruit_ccs811.CCS811(self._i2c)
        self.starting_time = datetime.now()
        LOGGER.debug("%s startedt at %s", self.NAME, self.starting_time)

    def get_measures(self) -> List[Measure]:
        time_passed_since_started = datetime.now() - self.starting_time
        if time_passed_since_started <= self.PAUSE_BEFORE_READING:
            LOGGER.debug(
                "Not ready to measure only %s passed since starting",
                time_passed_since_started
            )
            return []
        if not self._ccs811.data_ready:
            return []
        tvoc_measure = Measure(
            self._ccs811.tvoc,
            datetime.now(),
            'ppb',
            SupportedDataTypes.TVOC
        )
        co2_measure = Measure(
            self._ccs811.eco2,
            datetime.now(),
            'ppm',
            SupportedDataTypes.CO2
        )
        return [tvoc_measure, co2_measure]

    def adjust(self, measures: List[Measure]):

        # according to datasheet, we shoudn't read/set baseline during warm up
        # period
        time_passed_since_started = datetime.now() - self.starting_time
        if time_passed_since_started <= self.PAUSE_BEFORE_READING:
            LOGGER.debug(
                "Not ready to read baseline only %s passed since starting",
                time_passed_since_started
            )
            return
        saved_baseline = self._get_baseline()

        # if we have saved baseline and didn't set it since the start of the sensor
        if not self.baseline_was_set_after_start and saved_baseline:
            LOGGER.info("Setting a saved baseline %d to %s", saved_baseline, self.NAME)
            self.baseline_was_set_after_start = True
            self._ccs811.baseline = saved_baseline
            return

        current_baseline = self._ccs811.baseline
        LOGGER.debug("Current baseline %d, saved baseline %d", current_baseline, saved_baseline)
        if saved_baseline is None or saved_baseline != current_baseline:
            self._save_baseline(current_baseline)
            LOGGER.info("Saving new baseline %d", current_baseline)

    def _save_baseline(self, baseline: int):
        with open(BASELINE_FILE, 'w') as fh:
            fh.write(str(baseline))

    def _get_baseline(self) -> Union[int, None]:
        baseline = None
        try:
            with open(BASELINE_FILE, 'r') as fh:
                baseline_str = fh.read()
                if baseline_str:
                    baseline = int(baseline_str)
        except FileNotFoundError:
            pass
        return baseline


base.register_sensor(CCS811Sensor)
