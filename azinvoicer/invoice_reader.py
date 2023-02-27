import logging
import pandas as pd

from azinvoicer.invoice_model import ModelComplianceLevel, MappingModel, MandatoryFields
from azinvoicer.iotools import IOTools
from azinvoicer.invoice_mappers import EnvironnementMapper


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

    __headerDict: dict = {"environnement": []}

    def __init__(self) -> None:
        self.__logger = logging.getLogger("InvoiceParser")

    def __getOutputHeader(self, level: ModelComplianceLevel, model: MappingModel) -> dict:

        outHeader: dict = dict()
        outHeader.update(self.__headerDict)
        for m in model.getMandatoryColumnNames():
            outHeader[m] = []
        if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
            for o in model.getOptionalColumnNames():
                outHeader[o] = []
        return outHeader

    def parseInputTable(self, level: ModelComplianceLevel, model: MappingModel, mapper:EnvironnementMapper , table: pd.DataFrame) -> list:

        parsed = pd.DataFrame(self.__getOutputHeader(level, model))
        # envTables: list = list()

        for index, row in table.iterrows():
            currency: str = row[model.getMandatoryColumnName(MandatoryFields.BILLING_CURRENCY)]
            billedCost: str = row[model.getMandatoryColumnName(MandatoryFields.BILLED_COST)]
            billingPeriodStart:str = row[model.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_START)]
            billingPeriodEnd:str = row[model.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_END)]
            billingPeriodEnd:str = row[model.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_END)]
            category:str = row[model.getMandatoryColumnName(MandatoryFields.METER_CATEGORY)]
            sku:str = row[model.getMandatoryColumnName(MandatoryFields.METER_NAME)]
            


            resourceGroupName:str = row[model.getMandatoryColumnName(MandatoryFields.RESOURCE_GROUP_NAME)]
            rgName = rgName + "wtf"

        return parsed
