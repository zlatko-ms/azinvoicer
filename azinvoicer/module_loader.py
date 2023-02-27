import importlib
import logging
import re


class InvoiceClassToLoad(object):

    __packageName: str
    __className: str

    def __init__(self, declaration: str) -> None:
        self.logger = logging.getLogger("InvoiceClassToLoad")
        parts: list = declaration.split(":")
        self.__packageName = parts[0]
        self.__className = parts[1]

    def getPackageName(self) -> str:
        return self.__packageName

    def getClassName(self) -> str:
        return self.__className

    @classmethod
    def isValidDeclaration(cts, declaration: str) -> bool:
        return re.match("([\w+|\.])+(\:)([\w]+)", declaration)


class InvoiceClassLoader(object):

    __logger = logging.getLogger("InvoiceClassLoader")

    @classmethod
    def loadClassInstance(cts, item: InvoiceClassToLoad) -> any:
        try:
            theModule = importlib.import_module(item.getPackageName())
            theClass = getattr(theModule, item.getClassName())
            return theClass()
        except:
            cts.__logger.error("unable to load module=" + item.getPackageName() + " class=" + item.getClassName())
            return None
