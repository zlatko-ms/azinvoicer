import logging
from azinvoicer.invoice_mappers import Environnement, EnvironnementMapper
from azinvoicer.module_loader import InvoiceClassToLoad, InvoiceClassLoader


class MapperChain(EnvironnementMapper):

    __mappers = list()

    def __init__(self, mappers: list) -> None:
        self.__logger = logging.getLogger("MapperChain")
        self.__mappers = self.__loadMappers(mappers)

    def __loadMappers(self, mappers: list) -> list:
        mapperInstances = list()

        for m in mappers:
            if InvoiceClassToLoad.isValidDeclaration(m):
                ctl: InvoiceClassToLoad = InvoiceClassToLoad(m)
                mapperInstance = InvoiceClassLoader.loadClassInstance(ctl)
                mapperInstances.append(mapperInstance)
            else:
                self.__logger.warn("ignoring invalid mapper declaration " + m)

        return mapperInstances

    def getEnvironnement(
        self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict
    ) -> Environnement:
        for m in self.__mappers:
            e: Environnement = m.getEnvironnement(serviceFamily, serviceName, skuName, regionName, resourceGroupName, tags)
            if e != Environnement.NA:
                self.__logger.debug("mapper " + m.__class__.__name__ + " returned an environnement")
                return e
        return Environnement.NA
