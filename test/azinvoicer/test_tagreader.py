import unittest

from azinvoicer.invoice_tagreader import TagReader


class TestTagReader(unittest.TestCase):
    def ensure_keyValuesOk(self, data: dict) -> None:
        self.assertTrue("me" in data.keys())
        self.assertTrue("you" in data.keys())
        self.assertEqual(data["me"], "dev")
        self.assertEqual(data["you"], "customer")

    def test_classic_json(self) -> None:
        # given a classic json string
        tags: str = '{ "me" : "dev", "you" : "customer" }'
        # when parsed by the tag reader
        data: dict = TagReader.getDictFromTags(tags)
        # then keys/values are correctly intepretted
        self.ensure_keyValuesOk(data)

    def test_doublequoted_json(self) -> None:
        # given a double quoted json string
        tags: str = '{ ""me"" : ""dev"", ""you"" : ""customer"" }'
        # when parsed by the tag reader
        data: dict = TagReader.getDictFromTags(tags)
        # then keys/values are correctly intepretted
        self.ensure_keyValuesOk(data)

    def test_doublequoted_irregular_json(self) -> None:
        # given a classic json string
        tags: str = '{ ""me"" : ""dev"", ""you"" : ""customer"", ""them"" : """" }'
        # when parsed by the tag reader
        data: dict = TagReader.getDictFromTags(tags)
        # then keys/values are correctly intepretted
        self.ensure_keyValuesOk(data)

    def test_doubloqutoed_irregular_json_singledoublequoted(self) -> None:
        # given a incomplete json string
        tags: str = '{ ""me"" : ""dev"", ""you"" : ""customer"", ""them"" : "" }'
        # when parsed by the tag reader
        data: dict = TagReader.getDictFromTags(tags)
        # then keys/values are correctly intepretted
        self.ensure_keyValuesOk(data)

    def test_doubloqutoed_nonformatted_json_singledoublequoted(self) -> None:
        # given a incomplete, non compliant json string
        tags: str = '""me"" : ""dev"", ""you"" : ""customer"", ""them"" : ""'
        # when parsed by the tag reader
        data: dict = TagReader.getDictFromTags(tags)
        # then keys/values are correctly intepretted
        self.ensure_keyValuesOk(data)
