#!/usr/bin/env python3
"""
keyctl.py

Command-line utility for easy management of the uploadkeys file.
"""

from pathlib import Path
import argparse
import logging
import random
import string


def genkey(length):
    key = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))
    return key


def savekey(key):
    if not Path("uploadkeys").is_file():
        logging.info("uploadkeys file doesn't exist, it will be created.")
    with open("uploadkeys", "a+") as keyfile:
        keyfile.write(str(key) + "\n")
    logging.debug("Saved a key to uploadkeys: {0}".format(key))


def rmkey(delkey):
    removedkey = False
    with open("uploadkeys", "r") as keyfile:
        allkeys = keyfile.readlines()
        logging.debug("Loaded all upload keys")
    allkeys = [x.strip("\n") for x in allkeys]
    logging.debug("Stripped keys")
    if delkey in allkeys:
        allkeys.remove(delkey)
        removedkey = True
        logging.debug("Removed one instance of the key")

    with open("uploadkeys", "w") as keyfile:
        for k in allkeys:
            keyfile.write(k + "\n")

    if removedkey:
        return True
    else:
        return False


def find_duplicates():
    with open("uploadkeys", "r") as keyfile:
        allkeys = keyfile.readlines()
        logging.debug("Read all keys")
    allkeys = [x.strip("\n") for x in allkeys]
    logging.debug("Stripped newlines")
    seen = set()
    ukeys = []
    dupkeys = []
    for x in allkeys:
        if x not in seen:
            ukeys.append(x)
            seen.add(x)
        else:
            dupkeys.append(x)
    return dupkeys


def get_keys():
    with open("uploadkeys", "r") as keyfile:  # load valid keys
        validkeys = keyfile.readlines()
    logging.debug("Read uploadkeys")
    validkeys = [x.strip("\n") for x in validkeys]
    logging.debug("Stripped newlines from validkeys")
    while "" in validkeys:
        validkeys.remove("")
    logging.debug("Removed blank keys")
    return validkeys



def cmd_list(args):
    validkeys = get_keys()

    print("List of upload keys:")
    for i in range(len(validkeys)):
        showkey = validkeys[i][:6]
        if len(validkeys[i]) > 6:
            showkey += "..."

        print("    [{0}] {1}".format(i+1, showkey))


def cmd_generate(args):
    k = genkey(args.length)
    logging.debug("Generated a new key: {0}".format(k))
    savekey(k)
    print("Your new key is: {0}".format(k))


def cmd_add(args):
    print("Please type/paste the key you would like to add.")
    akr = input("> ")
    ak = akr.strip()
    print()
    logging.debug("Ran strip() on key")
    print(ak)
    if input("Is the above key correct? [y/N] ").lower() == "y":
        logging.debug("Interpreted as yes")
        ask_for_key = False
        savekey(ak)
        logging.info("Added.")
    else:
        logging.debug("Interpreted as no")
        print("No key has been saved.")


def cmd_remove(args):
    if rmkey(args.key):
        logging.debug("Successfully removed the requested key")
    else:
        logging.info("No key was removed.")

def cmd_dedupe(args):
    for d in find_duplicates():
        r = rmkey(d)
        logging.debug(r)
        logging.info("Removed duplicate key: {0}".format(d))
    else:
        logging.info("[" + u"\u2713" + "] No duplicate keys found!")

def cmd_show(args):
    for k in get_keys():
        if k[:6] == args.prefix:
            print("Key: {0}".format(k))
            break


parser = argparse.ArgumentParser()  # create instance of argument parser class

parlog = parser.add_mutually_exclusive_group()
parlog.add_argument("-v", "--verbose", help="show debugging messages", action="store_true")
parlog.add_argument("-q", "--quiet", help="show only warning messages and up", action="store_true")

subparsers = parser.add_subparsers(help="sub-commands")
parser_list = subparsers.add_parser("list", help="list the beginning of each key")
parser_list.set_defaults(func=cmd_list)

parser_gen = subparsers.add_parser("generate", help="generate a key and save it to uploadkeys")
parser_gen.add_argument("length", help="length of key to generate", default=64, type=int, nargs="?")
parser_gen.set_defaults(func=cmd_generate)

parser_add = subparsers.add_parser("add", help="prompts for a key to add to uploadkeys")
parser_add.set_defaults(func=cmd_add)

parser_remove = subparsers.add_parser("remove", help="remove (one instance of) a key from uploadkeys")
parser_remove.add_argument("key", help="key to remove")
parser_remove.set_defaults(func=cmd_remove)

parser_dedupe = subparsers.add_parser("dedupe", help="remove duplicate keys")
parser_dedupe.set_defaults(func=cmd_dedupe)

parser_show = subparsers.add_parser("show", help="show the full key based on the first 6 characters")
parser_show.add_argument("prefix", help="first 6 characters of key (shown by `python3 keyctl.py list`)")
parser_show.set_defaults(func=cmd_show)


args = parser.parse_args()  # parse the arguments

if args.verbose:
    loglevel = logging.DEBUG
elif args.quiet:
    loglevel = logging.WARNING
else:
    loglevel = logging.INFO
logging.basicConfig(level=loglevel, format="%(levelname)s: %(message)s")

try:
    args.func(args)
except AttributeError:
    logging.error("AttributeError")
    parser.print_help()
