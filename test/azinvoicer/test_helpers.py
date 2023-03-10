import unittest
import datetime
import shutil
import logging
import tempfile
import os

from azinvoicer.helpers import DateHelper, IOHelper


class TestDateHelper(unittest.TestCase):
    def test_DateFromString(self) -> None:
        # given a date as a string as well a date format
        format: str = "%m/%d/%Y"
        dateStr: str = "02/03/2023"

        # when I convert the date to dateformat
        date: datetime = DateHelper.parseDate(format, dateStr)

        # then all the informations are accurate
        self.assertEquals(date.date().day, 3)
        self.assertEquals(date.date().month, 2)
        self.assertEquals(date.date().year, 2023)

    def test_DateToString(self) -> None:
        # given a date as a dateformat
        date = datetime.date(2023, 12, 28)
        # and the desired string format
        format: str = "%m/%d/%Y"

        # when printing the date to the format
        dateStr: str = DateHelper.formatDate(format, date)

        # we get the accurate string
        self.assertEqual("12/28/2023", dateStr)

    def test_DateDeltaInDays(self) -> None:

        # given two dates distant of 2 days
        date1: datetime = datetime.date(2023, 12, 28)
        date2: datetime = datetime.date(2023, 12, 26)

        # when we compute the diff in days
        days: int = DateHelper.periodDays(date2, date1)

        # then we get 2 days
        self.assertEqual(days, 2)


class TestIOTools(unittest.TestCase):

    __testTempDirPath: str

    def setUp(self):
        self.__logger = logging.getLogger("TestIOTools")
        self.__testTempDirPath = tempfile.mkdtemp()

    def test_listToFile(self) -> None:
        # given a set of lines in an array
        maxLines: int = 10
        lines = list()
        for i in range(maxLines):
            lines.append("TESTLINE42")
        # and a path to to a temp file
        fileOut = os.path.join(self.__testTempDirPath, "outfile.csv")
        # when we request the array to be written to a file via IOTools
        IOHelper.listToFile(lines, fileOut)
        file_stats = os.stat(fileOut)
        num_lines = sum(1 for line in open(fileOut))
        # then the file is not empty
        self.assertGreater(file_stats.st_size, 0, "file is not empty")
        # and the number of lines in the file equals to the number of items in the array
        self.assertEqual(num_lines, maxLines, "file has all lines")

    def test_getFileSize(self) -> None:

        # given a file of a given size
        maxLines: int = 10240
        lines = list()
        for i in range(maxLines):
            lines.append("TESTLINE42")
        # and the path to that file
        fileOut = os.path.join(self.__testTempDirPath, "outfileSize.csv")
        IOHelper.listToFile(lines, fileOut)
        # when requesitng the file size from IOTools
        fsize: float = IOHelper.getFileSize(fileOut)
        # it returns the correct size
        self.assertEqual(fsize, 0.11, "file is correctly sized")

    def tearDown(self) -> None:
        shutil.rmtree(self.__testTempDirPath)


if __name__ == "__main__":
    unittest.main()
