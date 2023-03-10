import unittest
import pandas as pd

from azinvoicer.helpers import DateHelper

from azinvoicer.invoice_reader import (
    InvoiceLoader,
    InvoiceParser,
    InvoiceStats,
)
from azinvoicer.invoice_model import (
    ModelComplianceLevel,
    MappingModel,
    OptionFlags,
    OutputModel,
)
from azinvoicer.invoice_mappers import EnvironnementMapper, BasicRGMapper, Environnement


class TestInvoiceLoaderConstants(object):

    FILE_DATA_STD_MANDATORY_AND_OPTIONAL = (
        "./test/azinvoicer/fixtures/invoices/std_mandatory_and_optional.csv"
    )
    FILE_DATA_STD_MANDATORY_ONLY = (
        "./test/azinvoicer/fixtures/invoices/std_mandatory.csv"
    )
    FILE_MODEL_STD = "./azinvoicer/models/in/standard.yaml"


class TestInvoiceLoader(unittest.TestCase):

    FILE_DATA_STD_MANDATORY_AND_OPTIONAL = (
        "./test/azinvoicer/fixtures/invoices/std_mandatory_and_optional.csv"
    )
    FILE_DATA_STD_MANDATORY_ONLY = (
        "./test/azinvoicer/fixtures/invoices/std_mandatory.csv"
    )
    FILE_MODEL_STD = "./azinvoicer/models/in/standard.yaml"

    def test_loading_mandatory_and_optional(self) -> None:
        # given the standard model
        model: MappingModel = MappingModel(TestInvoiceLoaderConstants.FILE_MODEL_STD)

        # and an invoicer loader
        loader: InvoiceLoader = InvoiceLoader()

        # when we request the loading of the file that matches mandatory and optional fields
        table: pd.DataFrame = loader.loadInvoice(
            ModelComplianceLevel.MANDATORY_AND_OPTIONAL,
            model,
            TestInvoiceLoaderConstants.FILE_DATA_STD_MANDATORY_AND_OPTIONAL,
        )

        # then all the mandatory columns are taken into acocunt
        for c in model.getMandatoryColumnNames():
            self.assertIn(c, table.columns)

        # and all the optional columns are taken into account
        for c in model.getOptionalColumnNames():
            self.assertIn(c, table.columns)

    def test_loading_mandatory_only(self) -> None:
        # given the standard model
        model: MappingModel = MappingModel(self.FILE_MODEL_STD)

        # and an invoicer loader
        loader: InvoiceLoader = InvoiceLoader()

        # when we request the loading of the file that matches mandatory and optional fields
        table: pd.DataFrame = loader.loadInvoice(
            ModelComplianceLevel.MANDATORY_ONLY,
            model,
            TestInvoiceLoaderConstants.FILE_DATA_STD_MANDATORY_ONLY,
        )

        # then all the mandatory columns are taken into acocunt
        for c in model.getMandatoryColumnNames():
            self.assertIn(c, table.columns)

        # and all the optional columns are not taken into account
        for c in model.getOptionalColumnNames():
            self.assertNotIn(c, table.columns)


class TestInvoiceParser(unittest.TestCase):
    def test_invoice_parse_add_env(self) -> None:
        # given an std mapping model
        model: MappingModel = MappingModel(TestInvoiceLoaderConstants.FILE_MODEL_STD)
        # and and invoice table loaded by the loader
        loader: InvoiceLoader = InvoiceLoader()
        invoiceTable: pd.DataFrame = loader.loadInvoice(
            ModelComplianceLevel.MANDATORY_AND_OPTIONAL,
            model,
            TestInvoiceLoaderConstants.FILE_DATA_STD_MANDATORY_AND_OPTIONAL,
        )
        dateFormat = model.getOption(OptionFlags.DATE_FORMAT)

        # when the invoice is parsed using a std rg mapper
        mapper: EnvironnementMapper = BasicRGMapper()
        reader: InvoiceParser = InvoiceParser()
        ret: InvoiceStats = reader.parseInputTableAndAddEnv(
            ModelComplianceLevel.MANDATORY_AND_OPTIONAL, model, mapper, invoiceTable
        )

        # then the stats are accurate
        self.assertEqual(ret.currency, "EUR")
        self.assertEqual(
            ret.startDate,
            DateHelper.parseDate(dateFormat, "01/01/2023"),
        )
        self.assertEqual(
            ret.endDate,
            DateHelper.parseDate(dateFormat, "01/31/2023"),
        )
        self.assertEqual(ret.parsedLines, 1)
        self.assertEqual(ret.parsedLinesWithoutEnv, 0)
        self.assertEqual(ret.totalBilled, 0.000506)
        self.assertEqual(ret.totalBilledEnvs, 0.000506)
        self.assertEqual(ret.billedDays, 30)

        # then check the data table and ensure the environement colum is correctly added
        t = ret.data
        self.assertEquals(
            t[OutputModel.getColumName(OutputModel.ENV_FIELD)][0],
            str(Environnement.TEST.name),
        )


if __name__ == "__main__":
    unittest.main()
