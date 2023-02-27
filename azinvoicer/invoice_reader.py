import logging
import pandas as pd

from azinvoicer.invoice_model import (
    ModelComplianceLevel,
    MappingModel,
    MandatoryFields,
    OutputModel,
    OptionalFields,
    OptionFlags,
)
from azinvoicer.iotools import IOTools
from azinvoicer.invoice_mappers import EnvironnementMapper, Environnement
import datetime


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


class ParserOutputBulder(object):

    START_DATE = "startDate"
    END_DATE = "endDate"
    NUMBER_OF_DAYS = "days"
    TOTAL_BILLED = "totalBilled"
    TOTAL_BILLED_ENVS = "totalBilledEnvs"
    CURRENCY = "currency"
    PARSED_LINES = "parsedLines"
    PARSED_LINES_WITHOUT_ENV = "parsedLinesWithoutEnv"
    LINES_WITHOUT_ENV = "indexesOfLinesWithoutEnv"

    TABLE = "data"

    @classmethod
    def build(
        cls,
        startDate: datetime,
        endDate: datetime,
        parsedLines: int,
        parsedLinesWithoutEnv: int,
        totalBilled: float,
        totalBilledEnvs: float,
        currency: str,
        data: pd.DataFrame,
    ) -> dict:
        ret: dict = dict()
        ret[cls.START_DATE] = startDate
        ret[cls.END_DATE] = endDate
        ret[cls.CURRENCY] = currency
        ret[cls.NUMBER_OF_DAYS] = DateTool.periodDays(startDate, endDate)
        ret[cls.TOTAL_BILLED] = totalBilled
        ret[cls.TOTAL_BILLED_ENVS] = totalBilledEnvs
        ret[cls.PARSED_LINES] = parsedLines
        ret[cls.PARSED_LINES_WITHOUT_ENV] = parsedLinesWithoutEnv
        ret[cls.TABLE] = data
        return ret


class DateTool(object):
    @classmethod
    def getDate(cls, inModel: MappingModel, dateInStr: str) -> datetime:
        return datetime.datetime.strptime(dateInStr, inModel.getOption(OptionFlags.DATE_FORMAT))

    @classmethod
    def periodDays(cls, start: datetime, end: datetime) -> int:
        delta = end - start
        return delta.days


class InvoiceParser(object):

    __headerDict: dict = {"environnement": []}

    def __init__(self) -> None:
        self.__logger = logging.getLogger("InvoiceParser")

    def __getOutputHeader(self, level: ModelComplianceLevel) -> dict:

        outHeader: dict = dict()
        outHeader.update(self.__headerDict)
        for m in MandatoryFields.ALL_FIELDS:
            cname = OutputModel.getColumName(m)
            outHeader[cname] = []
        if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
            for o in OptionalFields.ALL_FIELDS:
                cname = OutputModel.getColumName(m)
                outHeader[cname] = []
        return outHeader

    def parseInputTable(
        self,
        level: ModelComplianceLevel,
        inModel: MappingModel,
        outModel: OutputModel,
        mapper: EnvironnementMapper,
        table: pd.DataFrame,
    ) -> dict:

        # create output data frame
        parsed = pd.DataFrame(self.__getOutputHeader(level, inModel))
        parsed[OutputModel.getColumName(MandatoryFields.BILLED_COST)] = parsed[
            OutputModel.getColumName(MandatoryFields.BILLED_COST)
        ].astype(float)

        # parsing result globals
        invoiceEndDate: datetime = datetime.datetime.strptime("03/02/1973", "%d/%m/%Y")
        invoiceStartDate: datetime = datetime.datetime.now()
        totalBilled: float = 0
        totalBilledEnvs: float = 0
        totalLinesParsed = 0
        totalLinesParsedWithoutEnv = 0
        linesWithoutEnv: list = list()

        for index, row in table.iterrows():

            currency: str = row[inModel.getMandatoryColumnName(MandatoryFields.BILLING_CURRENCY)]
            billedCost: str = row[inModel.getMandatoryColumnName(MandatoryFields.BILLED_COST)]
            billingPeriodStart: str = row[inModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_START)]
            billingPeriodEnd: str = row[inModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_END)]
            family: str = row[inModel.getMandatoryColumnName(MandatoryFields.SERVICE_FAMILY)]
            category: str = row[inModel.getMandatoryColumnName(MandatoryFields.METER_CATEGORY)]
            sku: str = row[inModel.getMandatoryColumnName(MandatoryFields.METER_NAME)]
            resourceGroupName: str = row[inModel.getMandatoryColumnName(MandatoryFields.RESOURCE_GROUP_NAME)]
            tags: str = row[inModel.getMandatoryColumnName(MandatoryFields.TAGS)]
            resourceLocation: str = row[inModel.getMandatoryColumnName(MandatoryFields.RESOURCE_LOCATION)]

            environnement: Environnement = mapper.getEnvironnement(
                family, category, sku, resourceLocation, resourceGroupName, tags
            )

            currIndex = len(parsed)
            parsed.loc[currIndex][outModel.getColumName("Environnement")] = environnement.name
            parsed.loc[currIndex][outModel.getColumName(MandatoryFields.SERVICE_FAMILY)] = family
            parsed.loc[currIndex][outModel.getColumName(MandatoryFields.METER_CATEGORY)] = category
            parsed.loc[currIndex][outModel.getColumName(MandatoryFields.METER_NAME)] = sku
            parsed.loc[currIndex][outModel.getColumName(MandatoryFields.BILLED_COST)] = float(billedCost)
            parsed.loc[currIndex][outModel.getColumName(MandatoryFields.BILLING_CURRENCY)] = currency

            partNum: str = None
            if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
                if inModel.getOption(OptionFlags.USE_PART_NUMBER):
                    partNum = row[inModel.getMandatoryColumnName(OptionalFields.PART_NUMBER)]
                    parsed.loc[currIndex][outModel.getColumName(OptionalFields.PART_NUMBER)] = partNum

            # check globals vs line info
            startDate: datetime = DateTool.getDate(inModel, billingPeriodStart)
            if startDate < invoiceStartDate:
                invoiceStartDate = startDate

            endDate: datetime = DateTool.getDate(inModel, billingPeriodEnd)
            if endDate > invoiceEndDate:
                invoiceEndDate = endDate

            totalLinesParsed = totalLinesParsed + 1
            totalBilled = totalBilled + float(billedCost)

            if environnement == Environnement.NA:
                totalLinesParsedWithoutEnv = totalLinesParsedWithoutEnv + 1
                linesWithoutEnv.append(str(index))
            else:
                totalBilledEnvs = totalBilledEnvs + float(billedCost)

        # build response payload
        return ParserOutputBulder.build(
            invoiceStartDate,
            invoiceEndDate,
            totalLinesParsed,
            totalLinesParsedWithoutEnv,
            totalBilled,
            totalBilledEnvs,
            currency,
            parsed,
        )
