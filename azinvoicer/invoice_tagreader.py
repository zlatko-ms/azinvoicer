import logging
import json
import re


class TagReader(object):

    logger = logging.getLogger("TagReader")

    @classmethod
    def getDictFromTags(cts, tags: str) -> dict:
        data: dict
        jsonForm: str = ""
        if '""' in tags:
            # strip double quotes enclosing strings
            a: str = re.sub(pattern=r'("")([\w]+)("")', repl='"\\2"', string=tags)
            # strip quadruple quotes (i.e empty value)
            b: str = a.replace('""""', '""')
            jsonForm = b
        else:
            jsonForm = tags

        if (not re.match("{", tags)) and (not re.match("}", tags)):
            jsonForm = "{" + jsonForm + "}"

        try:
            data = json.loads(jsonForm)
        except Exception as ex:
            data = dict()
            cts.logger.debug("error while parsing tags from json : " + jsonForm + " error=" + getattr(ex, "message", repr(ex)))
        return data
