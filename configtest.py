import os
import settings as settings


# Default settings
defaults = {
    "UPLOAD_FOLDER": "/var/www/img",
    "ALLOWED_EXTENSIONS": [".png", ".jpg", ".jpeg", ".svg", ".bmp", ".gif", ".ico",  ".webp"],
    "ROOTURL": "https://img.bbaovanc.com/",
    "SAVELOG": "savelog.log",
    "SAVELOG_CHMOD": "0o644",
    "SAVELOG_KEYPREFIX": 4,
}

deftypes = {
    "UPLOAD_FOLDER": str,
    "ALLOWED_EXTENSIONS": list,
    "ROOTURL": str,
    "SAVELOG": str,
    "SAVELOG_CHMOD": int,
    "SAVELOG_KEYPREFIX": int,
}


# Check for unset settings
checksettings = list(defaults.keys())
unset_settings = [i for i in defaults.keys() if i not in dir(settings)]
if len(unset_settings) > 0:
    for unset in unset_settings:
        checksettings.remove(unset)
        print("[!] {0} is unset. The default value is type {1} with value {2}".format(unset, deftypes[unset].__name__, defaults[unset]))
else:
    print("[" + u"\u2713" + "] Found all required settings!")


# Check if types of settings are correct
typesgood = True
typeswrong = []
for testtype in checksettings:
    if type(getattr(settings, testtype)) is not deftypes[testtype]:
        print("[!] {0} requires {1}, but is {2}".format(testtype, deftypes[testtype].__name__, type(getattr(settings, testtype)).__name__))
        typeswrong.append(testtype)
        typesgood = False

if typesgood:
    print("[" + u"\u2713" + "] Types are good!")


# Check if allowed extensions all start with a .
invalid_exts = []
if "ALLOWED_EXTENSIONS" in checksettings:
    for e in settings.ALLOWED_EXTENSIONS:
        if not e.startswith("."):
            invalid_exts.append(e)

    if len(invalid_exts) > 0:
        print("[!] The following extensions listed in ALLOWED_EXTENSIONS are invalid:")
        for e in invalid_exts:
            print("    {0} is listed in ALLOWED_EXTENSIONS, but doesn't start with a .".format(e))
    else:
        print("[" + u"\u2713" + "] ALLOWED_EXTENSIONS is good!")


# Check if UPLOAD_FOLDER exists
uploadfolder_exists = True
if "UPLOAD_FOLDER" in checksettings:
    if not os.path.isdir(settings.UPLOAD_FOLDER):
        uploadfolder_exists = False
        print("[!] The directory set in UPLOAD_FOLDER ('{0}') doesn't exist!".format(settings.UPLOAD_FOLDER))
    else:
        print("[" + u"\u2713" + "] UPLOAD_FOLDER exists!")


# Check if ROOTURL starts with http(s):// and ends with /
rooturl_good = True
if "ROOTURL" in checksettings:
    if settings.ROOTURL.startswith("http://") or settings.ROOTURL.startswith("https://"):
        pass
    else:
        rooturl_good = False
        print(settings.ROOTURL)
        print(settings.ROOTURL.startswith("https://"))
        print("[!] ROOTURL does not start with `http://` or `https://`! This may cause issues!")
    if not settings.ROOTURL.endswith("/"):
        rooturl_good = False
        print("[!] ROOTURL does not end with a `/`. This WILL cause issues!")

    if not rooturl_good:
        print("    With your current settings, this is what a generated url would look like:")
        print("    {0}example.png".format(settings.ROOTURL))
    else:
        print("[" + u"\u2713" + "] ROOTURL is good!")


# Ask the user if SAVELOG is the intended filename
if "SAVELOG" in checksettings:
    print("[*] SAVELOG was interpreted to be {0}".format(settings.SAVELOG))
    print("[*] If this is not the intended filename, please fix it.")


# Show summary
print()
print("----- SUMMARY -----")
summarygood = True
if len(unset_settings) > 0:
    summarygood = False
    print("Unset settings:")
    for unset in unset_settings:
        print("    {0}".format(unset))

if len(typeswrong) > 0:
    summarygood = False
    print("Incorrect types:")
    for wtype in typeswrong:
        print("    {0}".format(wtype))

if len(invalid_exts) > 0:
    summarygood = False
    print("Invalid extensions:")
    for wext in invalid_exts:
        print("    '{0}'".format(wext))

if not uploadfolder_exists:
    summarygood = False
    print("UPLOAD_FOLDER ({0}) does not exist!".format(settings.UPLOAD_FOLDER))

if not rooturl_good:
    summarygood = False
    print("ROOTURL may cause issues!")
    print("With current settings, this is what a generated URL would look like:")
    print("{0}example.png".format(settings.ROOTURL))

if "SAVELOG" in checksettings:
    print("[*] SAVELOG is {0}".format(settings.SAVELOG))

if summarygood:
    print("[" + u"\u2713" + "] This configuration passes all tests!")
