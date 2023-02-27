import unittest

from azinvoicer.invoice_mapperchain import MapperChain
from azinvoicer.invoice_mappers import EnvironnementMapper, Environnement

class DummyMapper(EnvironnementMapper):

    def getEnvironnement(self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict) -> Environnement:
        return Environnement.NA

class SandboxMapper(EnvironnementMapper):

    def getEnvironnement(self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict) -> Environnement:
        return Environnement.SANDBOX

class TestMapperChain(unittest.TestCase):

    def test_chain(self) -> None:
        # given a mapper chain
        items=[ "test.azinvoicer.test_mapperchain:DummyMapper", "test.azinvoicer.test_mapperchain:SandboxMapper" ]
        chain:MapperChain = MapperChain(items)
        # when retrienving evnironnement
        e:Environnement = chain.getEnvironnement("whatever","whatever","whatever","whatever","whatever",dict())
        # we get the result the only non NA chain item returns
        self.assertEqual(e,Environnement.SANDBOX)

