import os
import logging
import datetime


class IOHelper(object):
    @classmethod
    def getFileSize(cts, fileName: str) -> float:
        file_stats = os.stat(fileName)
        mbSize = file_stats.st_size / (1024 * 1024)
        mbSizeRounded = round(mbSize, 2)
        return mbSizeRounded

    @classmethod
    def mkdir(cts, dirPath: str) -> None:
        os.makedirs(dirPath, exist_ok=True)

    @classmethod
    def mkdirFilePath(cts, filePath: str) -> None:
        os.makedirs(os.path.dirname(filePath), exist_ok=True)

    @classmethod
    def listToFile(cts, items: set, filePath: str) -> None:
        with open(filePath, "w") as f:
            for line in items:
                f.write(line + "\n")
            f.close()


class DateHelper(object):
    @classmethod
    def parseDate(cls, dateFormat: str, dateInStr: str) -> datetime:
        return datetime.datetime.strptime(dateInStr, dateFormat)

    @classmethod
    def periodDays(cls, start: datetime, end: datetime) -> int:
        delta = end - start
        return delta.days

    @classmethod
    def formatDate(cls, dateFormat: str, dateInDt: datetime) -> str:
        return datetime.datetime.strftime(dateInDt, dateFormat)
