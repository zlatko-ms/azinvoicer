import unittest
import tempfile
import os
import shutil
import logging

from azinvoicer.iotools import IOTools


class TestIOTools(unittest.TestCase):

    __testTempDirPath: str
    __tools: IOTools

    def setUp(self):
        self.__tools = IOTools()
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
        self.__tools.listToFile(lines, fileOut)
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
        self.__tools.listToFile(lines, fileOut)
        # when requesitng the file size from IOTools
        fsize: float = self.__tools.getFileSize(fileOut)
        # it returns the correct size
        self.assertEqual(fsize, 0.11, "file is correctly sized")

    def tearDown(self) -> None:
        shutil.rmtree(self.__testTempDirPath)


if __name__ == "__main__":
    unittest.main()
