#!/usr/bin/env python3
"""
imgupload.py

Flask application for processing images uploaded through POST requests.
"""

from flask import Flask, request, jsonify
from flask_api import status
from flask.helpers import send_file
from pathlib import Path
import os
import datetime
from PIL import Image
import re

import settings  # app settings (such as allowed extensions)
import functions  # custom functions

app = Flask(__name__)  # app is the app


def allowed_extension(testext):
    if testext.lower() in settings.ALLOWED_EXTENSIONS:
        return True
    else:
        return False


def log_savelog(key, ip, savedname):
    if settings.SAVELOG_KEYPREFIX > 0:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {key[:settings.SAVELOG_KEYPREFIX]}: {ip} - {savedname}\n")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)
    else:
        with open(settings.SAVELOG, "a+") as slogf:
            slogf.write(f"[{datetime.datetime.now()}] {ip} - {savedname}\n")
        os.chmod(settings.SAVELOG, settings.SAVELOG_CHMOD)


class EncodeDecodeError(Exception):
    pass

def utf8_decode_filename(filename):
    s = filename.replace(u"\u200b", "0").replace(u"\u200c", "1")
    if not re.compile("^[01]+$").match(s):
        raise EncodeDecodeError
    decstr = ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8))
    return decstr


def utf8_encode_filename(filename):
    fname_bin = ''.join('{:08b}'.format(b) for b in filename.encode('utf-8'))
    fname_txt = fname_bin.replace('0', u'\u200b').replace('1', u'\u200c')
    return fname_txt


@app.route("/encode/<decoded_url>", methods = ["GET"])
def encode(decoded_url):
    return utf8_encode_filename(decoded_url)


@app.route("/decode/<encoded_url>", methods = ["GET"])
def decode(encoded_url):
    return utf8_decode_filename(encoded_url)


@app.route("/utf8/<encoded_url>", methods = ["GET"])
def utf8(encoded_url):
    print("Received /utf8/ request")
    try:
        decstr = utf8_decode_filename(encoded_url)
    except EncodeDecodeError:
        print("filename doesn't contain only 200b and 200c")
        return jsonify({'status': 'error', 'error': 'NOT_FOUND'}), status.HTTP_404_NOT_FOUND

    imgpath = Path(os.path.join(settings.UPLOAD_FOLDER, decstr))
    if imgpath.is_file():
        return send_file(imgpath)
    else:
        print(f"Not a file: {imgpath}")
        return jsonify({'status': 'error', 'error': 'NOT_FOUND'}), status.HTTP_404_NOT_FOUND

@app.route("/upload", methods = ["POST"])
def upload():
    if request.method == "POST":  # sanity check: make sure it's a POST request
        print("Request method was POST!")

        with open("uploadkeys", "r") as keyfile:  # load valid keys
            validkeys = keyfile.readlines()
        validkeys = [x.strip("\n") for x in validkeys]
        while "" in validkeys:
            validkeys.remove("")
        print("Loaded validkeys")

        if "uploadKey" in request.form:  # if an uploadKey was provided
            if request.form["uploadKey"] in validkeys:  # check if uploadKey is valid
                print("Key is valid!")

                if "verify" in request.form.keys():
                    if request.form["verify"] == "true":
                        print("Request is asking if key is valid (it is)")
                        return jsonify({'status': 'key_valid'})

                if "imageUpload" in request.files:  # check if image to upload was provided
                    f = request.files["imageUpload"]  # f is the image to upload
                else:
                    print("No image upload was found!")
                    return jsonify({'status': 'error', 'error': 'NO_IMAGE_UPLOADED'}), status.HTTP_400_BAD_REQUEST

                if f.filename == "":  # make sure the filename isn't blank
                    print("Filename is blank")
                    return jsonify({'status': 'error', 'error': 'FILENAME_BLANK'}), status.HTTP_400_BAD_REQUEST

                fext = Path(f.filename).suffix  # get the uploaded extension
                if allowed_extension(fext):  # if the extension is allowed
                    if not "imageName" in request.form.keys():
                        print(f"Generating file with extension {fext}")
                        fname = functions.generate_name() + fext  # generate file name
                        print(f"Generated name: {fname}")
                    else:
                        fname = request.form["imageName"]
                        if len(fname) > 0:
                            print(f"Request imageName: {fname}")
                            if not fname.lower().endswith(fext.lower()):  # if requested name doesn't have the correct extension
                                fname += fext  # add the extension
                                print(f"Added extension; new filename: {fname}")
                        else:
                            print("Requested filename is blank!")
                            fname = functions.generate_name() + fext  # generate a valid filename
                            print(f"Generated name: {fname}")

                    if f:  # if the uploaded image exists
                        print("Uploaded image exists")
                        if Path(os.path.join(settings.UPLOAD_FOLDER, fname)).is_file():
                            print("Requested filename already exists!")
                            return jsonify({'status': 'error', 'error': 'FILENAME_TAKEN'}), status.HTTP_409_CONFLICT

                        f.save(f"/tmp/{fname}")  # save the image temporarily (before removing EXIF)
                        image = Image.open(f"/tmp/{fname}")
                        data = list(image.getdata())
                        stripped = Image.new(image.mode, image.size)
                        stripped.putdata(data)
                        stripped.save(os.path.join(settings.UPLOAD_FOLDER, fname))  # save the image without EXIF

                        print(f"Saved to {fname}")
                        url = settings.ROOTURL + fname  # construct the url to the image
                        path_txt = utf8_encode_filename(fname)
                        utf8_url = settings.ROOTURL + "utf8/" + path_txt
                        if settings.SAVELOG != "/dev/null":
                            print("Saving to savelog")
                            log_savelog(request.form["uploadKey"], request.remote_addr, fname)
                        print("Returning json response")
                        return jsonify({'status': 'success',
                                        'url': url,
                                        'utf8_url': utf8_url,
                                        'name': fname,
                                        'uploadedName': f.filename,
                                        }), status.HTTP_201_CREATED
                    else:  # this shouldn't happen
                        print("Um... uploaded image... is nonexistent? Please report this error!")
                        return jsonify({'status': 'error', 'error': 'UPLOADED_IMAGE_FAILED_SANITY_CHECK_1'}), status.HTTP_400_BAD_REQUEST

                else:  # if the extension was invalid
                    print("Uploaded extension is invalid!")
                    return jsonify({'status': 'error', 'error': 'INVALID_EXTENSION'}), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

            else:  # if the key was not valid
                print("Key is invalid!")
                print(f"Request key: {request.form['uploadKey']}")
                return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED

        else:  # if uploadKey was not found in request body
            print("No uploadKey found in request!")
            return jsonify({'status': 'error', 'error': 'UNAUTHORIZED'}), status.HTTP_401_UNAUTHORIZED
    else:
        print("Somehow the request method was not POST!")
        return jsonify({'status': 'error', 'error': 'WRONG_METHOD'}), status.HTTP_405_METHOD_NOT_ALLOWED

if __name__ == "__main__":
    print("Run with `flask` or a WSGI server!")
