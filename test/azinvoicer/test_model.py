import unittest

from azinvoicer.invoice_model import MandatoryFields, OptionalFields, MappingModel, OptionFlags, MappingModelRepository, ModelComplianceChecker, ModelCompliancePicker, ModelCompliancePick, ModelComplianceLevel


class ModelTestConstants(object):
    PATH_TO_TEST_REPO = "./azinvoicer/repo/models"
    STD_MODEL = "./azinvoicer/repo/models/standard.yaml"


class TestMappingModel(unittest.TestCase):

    __TEST_FILE = "standard.yaml"

    def test_init_fromFile(self) -> None:

        # given a model file
        filePath: str = ModelTestConstants.PATH_TO_TEST_REPO+"/"+self.__TEST_FILE

        # when I instanciate a model from that file
        mappingModel: MappingModel = MappingModel(filePath)

        # then the name is correctly extracted from path
        self.assertEqual("standard", mappingModel.getName(), "name is consistent")

        # and I get the mandatory mappings as declared in the file
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.TAGS), 'Tags', "tags mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.METER_CATEGORY), 'MeterCategory', "meterCategory mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.METER_NAME), 'MeterName', "meterName mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.RESOURCE_LOCATION), 'ResourceLocation', "resourceLocation mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.BILLED_COST), 'CostInBillingCurrency', "costInBillingCurrency mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.BILLING_CURRENCY), 'BillingCurrency', "billingCurrency mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.RESOURCE_GROUP_NAME), 'ResourceGroupName', "resourceGroupName mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_START), 'BillingPeriodStartDate', "billingPeriodStartDate mapping is accurate")
        self.assertEqual(mappingModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_END), 'BillingPeriodEndDate', "billingPeriodEndDate mapping is accurate")

        # and I get the optional mappings as declared in the file
        self.assertEqual(mappingModel.getOptionalColumnName(OptionalFields.LOCATION), 'Location', "location mapping is accurate")
        self.assertEqual(mappingModel.getOptionalColumnName(OptionalFields.PART_NUMBER), 'PartNumber', "partNumber mapping is accurate")
        self.assertEqual(mappingModel.getOptionalColumnName(OptionalFields.ADDITIONAL_INFO), 'AdditionalInfo', "additionalInfo mapping is accurate")

        # and I get the options as declared in the file
        self.assertEqual(mappingModel.getOption(OptionFlags.USE_ADDITIONAL_INFO), False, "option additional info is accurate")
        self.assertEqual(mappingModel.getOption(OptionFlags.USE_LOCATION), False, "option location is accurate")
        self.assertEqual(mappingModel.getOption(OptionFlags.USE_PART_NUMBER), False, "option part number info is accurate")

    def test_list_mandatory(self) -> None:
        # given a model descrition file
        filePath: str = ModelTestConstants.PATH_TO_TEST_REPO + "/" + self.__TEST_FILE
        # and a model from that file
        mappingModel: MappingModel = MappingModel(filePath)
        # when listing mandatory fields
        mandatory: list = mappingModel.getMandatoryColumnNames()
        # then all the mandatory fields are provided
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.TAGS), mandatory, "tags is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.METER_CATEGORY), mandatory, "meterCategory mapping is")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.METER_NAME), mandatory, "meterName is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.RESOURCE_LOCATION), mandatory, "resourceLocation is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.BILLED_COST), mandatory, "costInBillingCurrency is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.BILLING_CURRENCY), mandatory, "billingCurrency is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.RESOURCE_GROUP_NAME), mandatory, "resourceGroupName is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_START), mandatory, "billingPeriodStartDate is provided as mandatory field")
        self.assertIn(mappingModel.getMandatoryColumnName(MandatoryFields.BILLING_PERIOD_END), mandatory, "billingPeriodEndDate is provided as mandatory field")

    def test_list_optional(self) -> None:
        # given a model descrition file
        filePath: str = ModelTestConstants.PATH_TO_TEST_REPO+"/"+self.__TEST_FILE
        # and a model from that file
        mappingModel: MappingModel = MappingModel(filePath)
        # when listing optional fields
        optional: list = mappingModel.getOptionalColumnNames()
        # then all the optional fields are provided
        self.assertIn(mappingModel.getOptionalColumnName(OptionalFields.LOCATION), optional, "location is provided as optional field")
        self.assertIn(mappingModel.getOptionalColumnName(OptionalFields.PART_NUMBER), optional, "partNumber is provided as optional field")
        self.assertIn(mappingModel.getOptionalColumnName(OptionalFields.ADDITIONAL_INFO), optional, "additionalInfo is provided as optional field")


class TestMappingModelRepo(unittest.TestCase):

    def test_models_loadFromPath(self) -> None:
        # given a repo path
        repoPath: str = ModelTestConstants.PATH_TO_TEST_REPO
        # when I load all the models from that path
        repo: MappingModelRepository = MappingModelRepository(repoPath)
        # then I get the accurate number or models loaded
        models = repo.listModelNames()
        self.assertEqual(len(models), 2, "two models were found and loaded")
        # and I get at least a stadard model
        self.assertTrue("standard" in models, "standard model was found and loaded")
        # and a standard_lc model
        self.assertTrue("standard_lc" in models, "standard_lc was found and loaded")


class InvoiceFixtures(object):
    TEST_FILE_MANDATORY_AND_OPTIONAL = "./test/azinvoicer/fixtures/invoices/std_mandatory_and_optional.csv"
    TEST_FILE_MANDATORY_ONLY = "./test/azinvoicer/fixtures/invoices/std_mandatory.csv"
    TEST_FILE_NOT_COMPLIANT = "./test/azinvoicer/fixtures/invoices/std_not_compliant.csv"


class TestModelComplianceChecker(unittest.TestCase):

    __stdModel: MappingModel

    def setUp(self):
        self.__stdModel: MappingModel = MappingModel(ModelTestConstants.STD_MODEL)

    def test_model_notCompliant(self) -> None:
        # given a model checker on a non std compliant file
        checker: ModelComplianceChecker = ModelComplianceChecker(InvoiceFixtures.TEST_FILE_NOT_COMPLIANT)
        # when we check the compliancy level
        level: ModelComplianceChecker = checker.getComplianceLevel(self.__stdModel)
        # then we get the correct compliancy level
        self.assertEqual(level.value, 0, "model is not compliant")

    def test_model_mandatoryOnly(self) -> None:
        # given a model checker on an std compliant file for mandatory fields only
        checker: ModelComplianceChecker = ModelComplianceChecker(InvoiceFixtures.TEST_FILE_MANDATORY_ONLY)
        # when we check the compliancy level
        level: ModelComplianceChecker = checker.getComplianceLevel(self.__stdModel)
        # then we get the correct compliancy level
        self.assertEqual(level.value, 1, "model is compliant with mandatory fields")

    def test_model_mandatoryAndOptional(self) -> None:
        # given a model checker on an std compliant file for mandatory and optional fields
        checker: ModelComplianceChecker = ModelComplianceChecker(InvoiceFixtures.TEST_FILE_MANDATORY_AND_OPTIONAL)
        # when we check the compliancy level
        level: ModelComplianceChecker = checker.getComplianceLevel(self.__stdModel)
        # then we get the correct compliancy level
        self.assertEqual(level.value, 2, "model is compliant with mandatory and optional fields")


class TestModelCompliancePicker(unittest.TestCase):

    def test_model_picker_on_std_mandatory(self) -> None:
        # given a repo containing all available models
        repo: MappingModelRepository = MappingModelRepository(ModelTestConstants.PATH_TO_TEST_REPO)
        # and a model picker
        picker: ModelCompliancePicker = ModelCompliancePicker()
        # when we ask for the best fitted model on a std compliant file
        bestPick: ModelCompliancePick = picker.getBestMatchingModel(repo, InvoiceFixtures.TEST_FILE_MANDATORY_AND_OPTIONAL)
        # then we get the std model with full compliance
        self.assertEqual(bestPick.getModel().getName(), "standard", "best fit model is the standard")
        self.assertEqual(bestPick.getLevel(), ModelComplianceLevel.MANDATORY_AND_OPTIONAL, "best fit complies with both mandatory and optional")

    def test_model_picker_on_non_compliant(self) -> None:
        # given a repo containing all available models
        repo: MappingModelRepository = MappingModelRepository(ModelTestConstants.PATH_TO_TEST_REPO)
        # and a model picker
        picker: ModelCompliancePicker = ModelCompliancePicker()
        # when we ask for the best fitted model on a std compliant file
        bestPick: ModelCompliancePick = picker.getBestMatchingModel(repo, InvoiceFixtures.TEST_FILE_NOT_COMPLIANT)
        # then we get the std model with full compliance
        self.assertEqual(bestPick.getModel(), None, "no best model for non compliant files")
        self.assertEqual(bestPick.getLevel(), ModelComplianceLevel.NOT_COMPLIANT, "not compliant files get a non compliant rating")

if __name__ == "__main__":
    unittest.main()
