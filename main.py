#!/usr/bin/python3

import logging

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)

logging.getLogger("main").info("Hello Python")
