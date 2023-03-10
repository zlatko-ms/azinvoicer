import logging
import pandas as pd

from azinvoicer.invoice_record import InvoiceRecord, InvoiceStats

from azinvoicer.invoice_model import (
    ModelComplianceLevel,
    MappingModel,
    MandatoryFields,
    OutputModel,
    OptionalFields,
    OptionFlags,
)

from azinvoicer.helpers import IOHelper, DateHelper
from azinvoicer.invoice_mappers import EnvironnementMapper, Environnement
import datetime


class InvoiceLoader(object):
    """reads the invoce according to a model"""

    def __init__(self) -> None:
        self.__logger = logging.getLogger("InvoiceLoader")

    def loadInvoice(
        self, level: ModelComplianceLevel, model: MappingModel, invoiceFilePath: str
    ) -> pd.DataFrame:

        # determine the columns to load according to compliance level
        columns = list()
        if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
            for col in model.getOptionalColumnNames():
                columns.append(col)
        for col in model.getMandatoryColumnNames():
            columns.append(col)

        # load only the necessary columns
        self.__logger.info(
            "loading invoice file "
            + invoiceFilePath
            + " size "
            + str(IOHelper.getFileSize(invoiceFilePath))
        )
        t = pd.read_csv(invoiceFilePath, skipinitialspace=True, usecols=columns)
        self.__logger.info("loaded invoice")
        return t


class InvoiceParser(object):

    __headerDict: dict = {"environnement": []}

    def __init__(self) -> None:
        self.__logger = logging.getLogger("InvoiceParser")

    def __getOutputHeader(self, level: ModelComplianceLevel) -> dict:

        outHeader: dict = {OutputModel.getColumName(OutputModel.ENV_FIELD): []}

        outHeader.update(self.__headerDict)
        for m in MandatoryFields.ALL_FIELDS:
            cname = OutputModel.getColumName(m)
            outHeader[cname] = []
        if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
            for o in OptionalFields.ALL_FIELDS:
                cname = OutputModel.getColumName(m)
                outHeader[cname] = []

        return outHeader

    def readAndGroup(
        self,
        level: ModelComplianceLevel,
        inModel: MappingModel,
        mapper: EnvironnementMapper,
        table: pd.DataFrame,
    ) -> dict:
        pass

    def parseInputTableAndAddEnv(
        self,
        level: ModelComplianceLevel,
        inModel: MappingModel,
        mapper: EnvironnementMapper,
        table: pd.DataFrame,
    ) -> InvoiceStats:

        # create output data frame
        parsed = pd.DataFrame(self.__getOutputHeader(level))
        parsed[OutputModel.getColumName(MandatoryFields.BILLED_COST)] = parsed[
            OutputModel.getColumName(MandatoryFields.BILLED_COST)
        ].astype(float)

        # parsing result globals
        invoiceEndDate: datetime = datetime.datetime.strptime("03/02/1973", "%d/%m/%Y")
        invoiceStartDate: datetime = datetime.datetime.now()
        totalBilled: float = 0
        totalBilledEnvs: float = 0
        totalLinesParsed: int = 0
        totalLinesParsedWithoutEnv: int = 0
        linesWithoutEnv: list = list()

        for index, row in table.iterrows():

            currency: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.BILLING_CURRENCY)
            ]
            billedCost: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.BILLED_COST)
            ]
            billingPeriodStart: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_START)
            ]
            billingPeriodEnd: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_END)
            ]
            family: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.SERVICE_FAMILY)
            ]
            category: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.METER_CATEGORY)
            ]
            sku: str = row[inModel.getMandatoryColumnName(MandatoryFields.METER_NAME)]
            resourceGroupName: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.RESOURCE_GROUP_NAME)
            ]
            tags: str = row[inModel.getMandatoryColumnName(MandatoryFields.TAGS)]
            resourceLocation: str = row[
                inModel.getMandatoryColumnName(MandatoryFields.RESOURCE_LOCATION)
            ]

            environnement: Environnement = mapper.getEnvironnement(
                family, category, sku, resourceLocation, resourceGroupName, tags
            )

            rowData: dict = {
                OutputModel.getColumName(OutputModel.ENV_FIELD): environnement.name,
                OutputModel.getColumName(MandatoryFields.SERVICE_FAMILY): family,
                OutputModel.getColumName(MandatoryFields.METER_CATEGORY): category,
                OutputModel.getColumName(MandatoryFields.METER_NAME): sku,
                OutputModel.getColumName(MandatoryFields.BILLED_COST): float(
                    billedCost
                ),
                OutputModel.getColumName(MandatoryFields.BILLING_CURRENCY): currency,
            }

            partNum: str = None
            if level == ModelComplianceLevel.MANDATORY_AND_OPTIONAL:
                if inModel.getOption(OptionFlags.USE_PART_NUMBER):
                    partNum = row[
                        inModel.getMandatoryColumnName(OptionalFields.PART_NUMBER)
                    ]
                    rowData[
                        OutputModel.getColumName(OptionalFields.PART_NUMBER)
                    ] = partNum

            parsed = parsed.append(rowData, ignore_index=True)
            # parsed = pd.concat(parsed, pd.DataFrame([rowData]))

            # check globals vs line info
            dateFormat: str = inModel.getOption(OptionFlags.DATE_FORMAT)
            startDate: datetime = DateHelper.parseDate(dateFormat, billingPeriodStart)
            if startDate < invoiceStartDate:
                invoiceStartDate = startDate

            endDate: datetime = DateHelper.parseDate(dateFormat, billingPeriodEnd)
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
        return InvoiceStats(
            startDate=invoiceStartDate,
            endDate=invoiceEndDate,
            parsedLines=totalLinesParsed,
            parsedLinesWithoutEnv=totalLinesParsedWithoutEnv,
            totalBilled=totalBilled,
            totalBilledEnvs=totalBilledEnvs,
            currency=currency,
            data=parsed,
            billedDays=DateHelper.periodDays(invoiceStartDate, invoiceEndDate),
        )
