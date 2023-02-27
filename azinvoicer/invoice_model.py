import os
import logging
import yaml
from yaml.loader import SafeLoader
from enum import Enum
import pandas as pd


class MandatoryFields(object):
    """mandatory fields keys"""

    SERVICE_FAMILY: str = "serviceFamily"
    METER_CATEGORY: str = "meterCategory"
    METER_NAME: str = "meterName"
    RESOURCE_LOCATION: str = "resourceLocation"
    BILLED_COST: str = "billedCost"
    BILLING_CURRENCY: str = "billingCurrency"
    TAGS: str = "tags"
    RESOURCE_GROUP_NAME: str = "resourceGroupName"
    BILLING_PERIOD_START: str = "billingPeriodStartDate"
    BILLING_PERIOD_END: str = "billingPeriodEndDate"

    ALL_FIELDS = [
        SERVICE_FAMILY,
        METER_CATEGORY,
        METER_NAME,
        RESOURCE_LOCATION,
        BILLED_COST,
        BILLING_CURRENCY,
        TAGS,
        RESOURCE_GROUP_NAME,
        BILLING_PERIOD_START,
        BILLING_PERIOD_END,
    ]


class OptionalFields(object):
    """optional fields keys"""

    LOCATION: str = "location"
    PART_NUMBER = "partNumber"
    ADDITIONAL_INFO: str = "additionalInfo"

    ALL_FIELDS = [LOCATION, PART_NUMBER, ADDITIONAL_INFO]


class OptionFlags(object):
    """option flags"""

    USE_LOCATION: str = "useLocation"
    USE_PART_NUMBER: str = "usePartNumber"
    USE_ADDITIONAL_INFO: str = "useAdditionalInfo"
    DATE_FORMAT: str = "dateFormat"


class ModelLoader(object):
    @classmethod
    def loadYamlFile(self, filePath: str) -> dict:
        with open(filePath, "r") as f:
            data = yaml.load(f, Loader=SafeLoader)
            return data


class MappingModel(object):
    """invoice column mapping model"""

    __modelData: dict = dict()
    __modelName: str

    def __init__(self, filePath: str) -> None:
        self.__logger = logging.getLogger("MappingModel")
        self.__modelData = ModelLoader.loadYamlFile(filePath)
        modelName = os.path.basename(filePath)
        self.__modelName = modelName.replace(".yaml", "").replace(".yml", "")

    def getMandatoryColumnName(self, fieldMappingConstant: str) -> str:
        return self.__modelData["model"]["mandatoryColumns"][fieldMappingConstant]

    def getOptionalColumnName(self, fieldMappingConstant: str) -> str:
        return self.__modelData["model"]["optionalColumns"][fieldMappingConstant]

    def getOption(self, optionName: str) -> str:
        if optionName == OptionFlags.DATE_FORMAT:
            if OptionFlags.DATE_FORMAT in self.__modelData.keys():
                return self.__modelData["options"][optionName]
            else:
                return "%m/%d/%Y"
        return self.__modelData["options"][optionName]

    def getMandatoryColumnNames(self) -> list:
        ret = list()
        for m in MandatoryFields.ALL_FIELDS:
            ret.append(self.getMandatoryColumnName(m))
        return ret

    def getOptionalColumnNames(self) -> list:
        ret = list()
        for o in OptionalFields.ALL_FIELDS:
            ret.append(self.getOptionalColumnName(o))
        return ret

    def getName(self) -> str:
        return self.__modelName


class OutputModel(object):
    """Provides column naming for intermediate and final models"""

    __modelData: dict = dict()

    def __init__(self, filePath: str) -> None:
        self.__logger = logging.getLogger("OutputModel")
        self.__modelData = ModelLoader.loadYamlFile(filePath)

    def getColumName(self, mappingName: str) -> str:
        return self.__modelData["model"]["columns_out"][mappingName]


class MappingModelRepository(object):
    """repository of all known mapping models read from a single directory location"""

    __models: dict = dict()

    def __init__(self, repoDirPath: str) -> None:
        self.__logger = logging.getLogger("MappingModelRepository")
        modelFiles = self.__listModelFilesFromRepo(repoDirPath)
        self.__models = self.__loadModelFilesFromRepo(modelFiles)

    def listModelNames(self) -> list:
        return list(self.__models.keys())

    def getModel(self, modelName: str) -> MappingModel:
        return self.__models[modelName]

    def __listModelFilesFromRepo(self, repoDirPath: str) -> list:
        files: list = list()
        for f in os.listdir(repoDirPath):
            if f.endswith(".yaml"):
                files.append(repoDirPath + "/" + f)
        return files

    def __loadModelFilesFromRepo(self, files: list) -> dict:
        modelsLoaded: dict = dict()
        for filePath in files:
            self.__logger.info("loading model from file " + filePath)
            model: MappingModel = MappingModel(filePath)
            modelsLoaded[model.getName()] = model
        return modelsLoaded


class ModelComplianceLevel(Enum):
    """level of compliance a given invoce had as regards to a given model"""

    NOT_COMPLIANT = 0
    MANDATORY_ONLY = 1
    MANDATORY_AND_OPTIONAL = 2


class ModelComplianceChecker(object):
    """computes the compliancy level of an invoice with a given model"""

    __columnsInFile: list
    __invoiceFilePath: str

    def __init__(self, invoiceFilePath: str) -> None:
        self.__invoiceFilePath = invoiceFilePath
        self.__logger = logging.getLogger("ModelComplianceChecker")
        self.__columnsInFile = self.__getColumnsFromFile(invoiceFilePath)

    def __getColumnsFromFile(self, invoiceFilePath: str) -> list:
        df: pd.DataFrame = pd.read_csv(invoiceFilePath, index_col=0, nrows=1)
        return df.columns.values.tolist()

    def getComplianceLevel(self, model: MappingModel) -> ModelComplianceLevel:

        mandatory: list = model.getMandatoryColumnNames()
        optional: list = model.getOptionalColumnNames()

        for m in mandatory:
            if m not in self.__columnsInFile:
                self.__logger.debug("unable to locate mandatory field " + m + " in file " + self.__invoiceFilePath)
                return ModelComplianceLevel.NOT_COMPLIANT

        for o in optional:
            if o not in self.__columnsInFile:
                self.__logger.debug("unable to locate optional field " + o + " in file " + self.__invoiceFilePath)
                return ModelComplianceLevel.MANDATORY_ONLY

        return ModelComplianceLevel.MANDATORY_AND_OPTIONAL


class ModelCompliancePick(object):

    __model: MappingModel
    __level: ModelComplianceLevel

    def __init__(self, model: MappingModel, level: ModelComplianceLevel) -> None:
        self.__model = model
        self.__level = level

    def getLevel(self) -> ModelComplianceLevel:
        return self.__level

    def getModel(self) -> MappingModel:
        return self.__model


class ModelCompliancePicker(object):
    """returns the most compliant model for a given invoice file"""

    def __init__(self) -> None:
        self.__logger = logging.getLogger("ModelCompliancePicker")

    def getBestMatchingModel(self, repo: MappingModelRepository, invoiceFilePath: str) -> ModelCompliancePick:
        levels = dict()
        availableModelNames: list = repo.listModelNames()
        checker: ModelComplianceChecker = ModelComplianceChecker(invoiceFilePath)
        for modelName in availableModelNames:
            model: MappingModel = repo.getModel(modelName)
            level: ModelComplianceLevel = checker.getComplianceLevel(model)
            levels[modelName] = level.value

        v = list(levels.values())
        k = list(levels.keys())
        maxKey = k[v.index(max(v))]

        if levels[maxKey] == 0:
            return ModelCompliancePick(None, ModelComplianceLevel.NOT_COMPLIANT)

        for e in ModelComplianceLevel:
            if e.value == levels[maxKey]:
                return ModelCompliancePick(repo.getModel(maxKey), e)
