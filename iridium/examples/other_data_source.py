from iridium.data.hdf5 import HDFData
from loguru import logger


class HDF5DataExample(HDFData):
    def map_data(self, row, instrument, from_time, to_time, data_frequency):
        logger.debug("mapping data from %s" % instrument)

