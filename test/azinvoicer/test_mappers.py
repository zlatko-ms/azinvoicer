import unittest

from azinvoicer.invoice_mappers import Environnement, TokenListMatcher, CommonMappingTokens, CommonStringMapper, BasicRGMapper

class TestCommonMappingTokens(unittest.TestCase):

    def test_mapping_prod(self) -> None:
         # for each token that matches prod, the mapper should return prod env
         self.assertTrue(CommonMappingTokens.isMatchingProd("prod"),"prod token is correctly matched")
         self.assertTrue(CommonMappingTokens.isMatchingProd("production"),"production token is correctly matched")
         self.assertTrue(CommonMappingTokens.isMatchingProd("Production"),"production token is correctly matched")
         self.assertTrue(CommonMappingTokens.isMatchingProd("PROD"),"PROD token is correctly matched")

    def test_mapping_preprod(self) -> None:
         # for each token that matches prod, the mapper should return prod env
         self.assertTrue(CommonMappingTokens.isMatchingPreProd("preprod"),"prod token is correctly matched")
         self.assertTrue(CommonMappingTokens.isMatchingPreProd("preproduction"),"production token is correctly matched")
         self.assertTrue(CommonMappingTokens.isMatchingPreProd("PreProduction"),"production token is correctly matched")
         self.assertTrue(CommonMappingTokens.isMatchingPreProd("PREPROD"),"PROD token is correctly matched")    


class TestCommonStringMapper(unittest.TestCase):

    def test_env_mappings(self) -> None:
        
        self.assertEqual(Environnement.PROD,CommonStringMapper.getEnvironnement("production"))
        self.assertEqual(Environnement.PREPRO,CommonStringMapper.getEnvironnement("pre-production"))
        self.assertEqual(Environnement.SANDBOX,CommonStringMapper.getEnvironnement("sndbx"))
        self.assertEqual(Environnement.STAGING,CommonStringMapper.getEnvironnement("stagingenv"))
        self.assertEqual(Environnement.TEST,CommonStringMapper.getEnvironnement("testing"))
        self.assertEqual(Environnement.DEMO,CommonStringMapper.getEnvironnement("demonstration"))
        self.assertEqual(Environnement.DEV,CommonStringMapper.getEnvironnement("developpement"))
        self.assertEqual(Environnement.INTERNAL,CommonStringMapper.getEnvironnement("internal"))
        self.assertEqual(Environnement.GLOBAL,CommonStringMapper.getEnvironnement("global env"))

class TestBasicRGMapper(unittest.TestCase):

    def test_rg_matching_envs(self) -> None:
        mapper=BasicRGMapper()
        self.assertEqual(Environnement.PROD,mapper.getEnvironnement("","","","","mycompany-071-prod",dict()))
        self.assertEqual(Environnement.PREPRO,mapper.getEnvironnement("","","","","mycompany-042-preprod",dict()))
        self.assertEqual(Environnement.SANDBOX,mapper.getEnvironnement("","","","","mycompany-042-sandbox",dict()))
        ## TBC ...


    def test_rg_not_matching_envs(self) -> None:
        mapper=BasicRGMapper()
        self.assertEqual(Environnement.NA,mapper.getEnvironnement("","","","","mycompany-071-porod",dict()))
        ## TBC ...



