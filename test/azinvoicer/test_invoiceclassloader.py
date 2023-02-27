import unittest
from azinvoicer.module_loader import InvoiceClassLoader, InvoiceClassToLoad


class TestInvoiceClassToLoad(unittest.TestCase):
    def test_validity_check_ok(self) -> None:
        # given a valid declaration
        toLoad = "azinvoicer.invoice_mappers:BasicRGMapper"
        # when checked, it is valid
        self.assertTrue(InvoiceClassToLoad.isValidDeclaration(toLoad))

    def test_validity_check_nok(self) -> None:
        # given an invalid declaration
        toLoad = "azinvoicer.invoice_mappers.BasicRGMapper"
        # when checked, it is valid
        self.assertFalse(InvoiceClassToLoad.isValidDeclaration(toLoad))

    def test_regular_naming(self) -> None:
        # given a regular declaration
        toLoad = "azinvoicer.invoice_mappers:BasicRGMapper"
        # when creating a load item
        icl: InvoiceClassToLoad = InvoiceClassToLoad(toLoad)
        # then the package name and classname are correctly extracted
        self.assertEqual(icl.getClassName(), "BasicRGMapper")
        self.assertEqual(icl.getPackageName(), "azinvoicer.invoice_mappers")


class TestInvoiceClassLoader(unittest.TestCase):
    def test_valid_classLoad(self) -> None:
        # given a valid class declaration
        toLoad = "azinvoicer.invoice_mappers:BasicRGMapper"
        # and an item represeing the class to load
        item: InvoiceClassToLoad = InvoiceClassToLoad(toLoad)
        # when required to load
        loaded = InvoiceClassLoader.loadClassInstance(item)
        # then the class is loaded
        self.assertFalse(loaded is None)
        # and the classname is exact
        self.assertEqual(loaded.__class__.__name__, "BasicRGMapper")
        # and the package name is exact
        self.assertEqual(loaded.__class__.__module__, "azinvoicer.invoice_mappers")

    def test_invalid_classLoad(self) -> None:
        # given a valid class declaration
        toLoad = "azinvoicer.invoice_mapperz:BasicRGMapper"
        # and an item represeing the class to load
        item: InvoiceClassToLoad = InvoiceClassToLoad(toLoad)
        # when required to load
        loaded = InvoiceClassLoader.loadClassInstance(item)
        # then the class is not loaded
        self.assertTrue(loaded is None)
