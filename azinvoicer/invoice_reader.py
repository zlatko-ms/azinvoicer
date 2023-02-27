import os
import logging
import yaml
from yaml.loader import SafeLoader
from enum import Enum
import pandas as pd

from azinvoicer.invoice_model import ModelComplianceLevel, MappingModel
from azinvoicer.iotools import IOTools


class InvoiceLoader(object):
    """reads the invoce according to a model"""

    def __init__(self) -> None:
        self.__logger = logging.getLogger("InvoiceLoader")

    def loadInvoice(self, level: ModelComplianceLevel, model: MappingModel, invoiceFilePath: str) -> pd.DataFrame:
        # determine the columns to load according to compliance level
        columns = list()
        if level == ModelComplianceLevel.MANDATORY_ONLY:
            for col in model.getMandatoryColumnNames():
                columns.append(col)
        if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
            for col in model.getOptionalColumnNames():
                columns.append(col)
        # load only the necessary columns
        self.__logger.info("loading invoice file " + InvoiceLoader + " size " + str(IOTools.getFileSize(invoiceFilePath)))
        t = pd.read_csv(invoiceFilePath, skipinitialspace=True, usecols=columns)
        self.__logger.info("loaded invoice")
        return t


class InvoiceParser(object):
    def __init__(self) -> None:
        self.__logger = logging.getLogger("InvoiceParser")

    def parseInputTable(self, table: pd.DataFrame) -> list:

        envTables: list = list()

        pass
