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

import settings


def log_savelog(key: str, ip: str, savedname: str) -> None:
    if settings.SAVELOG_KEYPREFIX > 0:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {key[:settings.SAVELOG_KEYPREFIX]}: {ip} - {savedname}\n")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)
    else:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {ip} - {savedname}\n")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)


def load_uploadkeys() -> list:
    with open("uploadkeys", "r") as keyfile:
        validkeys = keyfile.readlines()  # load valid keys

    validkeys = [x.strip("\n") for x in validkeys]  # remove newlines
    while "" in validkeys:
        validkeys.remove("")  # remove blank keys

    return validkeys


def save_and_strip_exif(f: FileStorage, fname: str) -> None:
    with tempfile.TemporaryFile() as tmpf:
        f.save(tmpf)  # save the image temporarily (before removing EXIF)

        image = Image.open(tmpf)
        data = list(image.getdata())
        stripped = Image.new(image.mode, image.size)
        stripped.putdata(data)
        stripped.save(os.path.join(settings.UPLOAD_FOLDER, fname))  # save the image without EXIF
