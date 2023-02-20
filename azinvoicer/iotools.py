import os
import logging


class IOTools(object):
    """just a set of file i/o helper subs"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("IOTools")

    def getFileSize(self, fileName) -> float:
        file_stats = os.stat(fileName)
        mbSize = file_stats.st_size / (1024 * 1024)
        mbSizeRounded = round(mbSize, 2)
        return mbSizeRounded

    def listToFile(self, items: set, filePath: str) -> None:
        with open(filePath, "w") as f:
            for line in items:
                f.write(line + "\n")
        f.close()
        self.logger.debug("wrote file " + filePath + " containing " + str(len(items)) + " line(s)")

    def mkdir(self, dirPath) -> None:
        os.makedirs(dirPath, exist_ok=True)
        self.logger.debug("created dir " + dirPath)

    def mkdirFilePath(self, filePath) -> None:
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
