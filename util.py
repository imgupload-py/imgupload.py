#!/usr/bin/env python3
"""
util.py

Various utilities for imgupload.py
"""


import os
import datetime

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
