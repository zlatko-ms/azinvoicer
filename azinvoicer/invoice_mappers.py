import re
import logging
from enum import Enum


class Environnement(Enum):
    """Environnement impacted by the invoice line"""

    NA = 0
    PROD = 1
    PREPRO = 2
    STAGING = 3
    TEST = 4
    DEV = 5
    DEMO = 6
    SANDBOX = 7
    INTERNAL = 8
    GLOBAL = 9


class EnvironnementMapper(object):
    def getEnvironnement(
        self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict
    ) -> Environnement:
        pass


class SingleEnvironnementMapper(EnvironnementMapper):
    def getEnvironnement(
        self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict
    ) -> Environnement:
        return Environnement.GLOBAL


class TokenListMatcher(object):
    @classmethod
    def isMatchingAnyToken(cls, item: str, tokens: list) -> bool:
        for token in tokens:
            if re.search(token, item, re.IGNORECASE):
                return True
        return False


class CommonMappingTokens(object):

    PROD_TOKENS = ["prod", "production", "prd"]
    PREPROD_TOKENS = ["preprod", "preproduction", "preprd", "pre-prod"]
    STAGING_TOKENS = ["staging"]
    TEST_TOKENS = ["testing", "test", "tst"]
    DEV_TOKENS = ["dev", "deve"]
    DEMO_TOKENS = ["demo", "show"]
    SANDBOX_TOKENS = ["sandbox", "sdb", "sndbx", "snd"]
    INTERNAL_TOKENS = ["internal", "enterprise", "int"]
    GLOBAL_TOKEN = ["global", "gbl"]

    @classmethod
    def isMatchingProd(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.PROD_TOKENS)

    @classmethod
    def isMatchingPreProd(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.PREPROD_TOKENS)

    @classmethod
    def isMatchingStaging(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.STAGING_TOKENS)

    @classmethod
    def isMatchingTest(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.TEST_TOKENS)

    @classmethod
    def isMatchingDemo(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.DEMO_TOKENS)

    @classmethod
    def isMatchingDev(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.DEV_TOKENS)

    @classmethod
    def isMatchingSandbox(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.SANDBOX_TOKENS)

    @classmethod
    def isMatchingInternal(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.INTERNAL_TOKENS)

    @classmethod
    def isMatchingGlobal(cls, item: str) -> bool:
        return TokenListMatcher.isMatchingAnyToken(item, CommonMappingTokens.GLOBAL_TOKEN)


class CommonStringMapper(object):
    @classmethod
    def getEnvironnement(cls, token: str) -> Environnement:

        if CommonMappingTokens.isMatchingPreProd(token):
            return Environnement.PREPRO

        if CommonMappingTokens.isMatchingProd(token):
            return Environnement.PROD

        if CommonMappingTokens.isMatchingTest(token):
            return Environnement.TEST

        if CommonMappingTokens.isMatchingStaging(token):
            return Environnement.STAGING

        if CommonMappingTokens.isMatchingDev(token):
            return Environnement.DEV

        if CommonMappingTokens.isMatchingDemo(token):
            return Environnement.DEMO

        if CommonMappingTokens.isMatchingSandbox(token):
            return Environnement.SANDBOX

        if CommonMappingTokens.isMatchingInternal(token):
            return Environnement.INTERNAL

        if CommonMappingTokens.isMatchingGlobal(token):
            return Environnement.GLOBAL

        return Environnement.NA


class BasicRGMapper(EnvironnementMapper):
    def __init__(self) -> None:
        self.logger = logging.getLogger("BasicRGMapper")

    def getEnvironnement(
        self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict
    ) -> Environnement:
        return CommonStringMapper.getEnvironnement(resourceGroupName)


class TagMatcher(object):

    TAGS_ENV_KEYS = ["SubscriptionScope", "Scope", "Env", "Environment"]

    @classmethod
    def getEnvKey(cls, tags: dict) -> str:
        for k in tags.keys():
            if TokenListMatcher.isMatchingAnyToken(k, TagMatcher.TAGS_ENV_KEYS):
                return k
        return None


class BasicTagsMapper(EnvironnementMapper):
    def __init__(self) -> None:
        self.logger = logging.getLogger("BasicRGMapper")

    def getEnvironnement(
        self, serviceFamily: str, serviceName: str, skuName: str, regionName: str, resourceGroupName: str, tags: dict
    ) -> Environnement:
        # check if there is any compelling key in the tags
        key: str = TagMatcher.getEnvKey(tags)
        if key is None:
            return Environnement.NA

        tagvalue = tags[key]
        return CommonStringMapper.getEnvironnement(tagvalue)
