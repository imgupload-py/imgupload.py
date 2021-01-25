#!/usr.bin/env python3
"""
encoding.py

Functions for encoding and decoding invisible urls.
"""


import re


class EncodeDecodeError(Exception):
    pass


def decode(filename):
    s = filename.replace(u"\u200b", "0").replace(u"\u200c", "1")  # convert to string of binary bits
    if not re.compile("^[01]+$").match(s):  # if it's not just ones and zeros
        raise EncodeDecodeError
    decstr = ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8))  # convert to text
    return decstr


def encode(filename):
    fname_bin = ''.join('{:08b}'.format(b) for b in filename.encode('utf-8'))  # convert text to string of ones and zeros
    fname_txt = fname_bin.replace('0', u'\u200b').replace('1', u'\u200c')  # replace ones and zeros with invisible chars
    return fname_txt
