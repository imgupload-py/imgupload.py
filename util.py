#!/usr/bin/env python3
"""
util.py

Various utilities for imgupload.py
"""


import os
import datetime
import tempfile
from PIL import Image
from werkzeug.datastructures import FileStorage

from app import logger as master_logger
import settings


util_logger = master_logger.getChild("util.py")


def log_savelog(key: str, ip: str, savedname: str) -> None:
    logger = util_logger.getChild("log_savelog()")
    if settings.SAVELOG_KEYPREFIX > 0:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {key[:settings.SAVELOG_KEYPREFIX]}: {ip} - {savedname}\n")
            logger.debug("Wrote to savelog with keyprefix")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)
        logger.debug("Ran chmod on savelog")
    else:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {ip} - {savedname}\n")
            logger.debug("Wrote to savelog without keyprefix")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)
        logger.debug("Ran chmod on savelog")


def load_uploadkeys() -> list:
    logger = util_logger.getChild("load_uploadkeys()")
    with open("uploadkeys", "r") as keyfile:
        validkeys = keyfile.readlines()  # load valid keys
        logger.debug("Read uploadkeys file")

    validkeys = [x.strip("\n") for x in validkeys]  # remove newlines
    logger.debug("Stripped all keys")
    while "" in validkeys:
        validkeys.remove("")  # remove blank keys
        logger.warn("Removed a blank key (blank line), you should probably remove this from the file for good!")

    return validkeys


def save_and_strip_exif(f: FileStorage, fname: str) -> None:
    logger = util_logger.getChild("save_and_strip_exif()")
    with tempfile.TemporaryFile() as tmpf:
        f.save(tmpf)  # save the image temporarily (before removing EXIF)
        logger.debug("Saved image temporarily")

        image = Image.open(tmpf)
        logger.debug("Opened image with PIL")
        data = list(image.getdata())
        logger.debug("Loaded image into PIL")
        stripped = Image.new(image.mode, image.size)
        logger.debug("Loaded image using PIL")
        stripped.putdata(data)
        logger.debug("Loaded image using PIL")
        stripped.save(os.path.join(settings.UPLOAD_FOLDER, fname))  # save the image without EXIF
        logger.debug("Loaded image using PIL")
