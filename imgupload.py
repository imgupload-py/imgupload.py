#!/usr/bin/env python3
"""
imgupload.py

Flask application for processing images uploaded through POST requests.
"""


from flask import Flask, request, jsonify, render_template, redirect
from flask_api import status

import os
import re
import datetime
from pathlib import Path
from PIL import Image

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
    s = filename.replace(u"\u200b", "0").replace(u"\u200c", "1")  # convert to string of binary bits
    if not re.compile("^[01]+$").match(s):  # if it's not just ones and zeros
        raise EncodeDecodeError
    decstr = ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8))  # convert to text
    return decstr


def utf8_encode_filename(filename):
    fname_bin = ''.join('{:08b}'.format(b) for b in filename.encode('utf-8'))  # convert text to string of ones and zeros
    fname_txt = fname_bin.replace('0', u'\u200b').replace('1', u'\u200c')  # replace ones and zeros with invisible chars
    return fname_txt


@app.route("/encode/<decoded_url>", methods = ["GET"])
def encode(decoded_url):
    return utf8_encode_filename(decoded_url)


@app.route("/decode/<encoded_url>", methods = ["GET"])
def decode(encoded_url):
    return utf8_decode_filename(encoded_url)


@app.route("/fancy/<image>", methods = ["GET"])
def fancy(image):
    try:
        decimg = utf8_decode_filename(image)
    except EncodeDecodeError:
        print("filename doesn't contain only 200b and 200c")
        return jsonify({'status': 'error', 'error': 'NOT_FOUND'}), status.HTTP_404_NOT_FOUND
    path = Path(os.path.join(settings.UPLOAD_FOLDER, decimg))  # create absolute path
    if path.is_file():  # if the image exists
        return redirect(settings.ROOTURL + decimg, 307)
    else:
        return jsonify({'status': 'error', 'error': 'NOT_FOUND'}), status.HTTP_404_NOT_FOUND


@app.route("/discord/<image>", methods = ["GET"])
def discord(image):
    try:
        decimg = utf8_decode_filename(image)
    except EncodeDecodeError:
        print("filename doesn't contain only 200b and 200c")
        return jsonify({'status': 'error', 'error': 'NOT_FOUND'}), status.HTTP_404_NOT_FOUND
    path = Path(os.path.join(settings.UPLOAD_FOLDER, decimg))  # create absolute path
    url = settings.ROOTURL + decimg  # create full url
    if path.is_file():  # if the image exists
        return render_template("i.html", url = url)
    else:
        return jsonify({'status': 'error', 'error': 'NOT_FOUND'}), status.HTTP_404_NOT_FOUND


@app.route("/upload", methods = ["POST"])
def upload():
    if request.method == "POST":  # sanity check: make sure it's a POST request
        print("Request method was POST!")

        with open("uploadkeys", "r") as keyfile:
            validkeys = keyfile.readlines()  # load valid keys
        validkeys = [x.strip("\n") for x in validkeys]  # remove newlines
        while "" in validkeys:
            validkeys.remove("")  # remove blank keys
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
                    if not "imageName" in request.form.keys():  # if an image name wasn't provided
                        print(f"Generating file with extension {fext}")
                        fname = functions.generate_name() + fext  # generate file name
                        print(f"Generated name: {fname}")
                    else:  # if a name was requested
                        fname = request.form["imageName"]  # get the requested image name
                        if len(fname) > 0:  # if the requested name isn't blank
                            print(f"Request imageName: {fname}")
                            if not fname.lower().endswith(fext.lower()):  # if requested name doesn't have the correct extension
                                fname += fext  # add the extension
                                print(f"Added extension; new filename: {fname}")
                        else:  # if the requested name is blank
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

                        path_txt = utf8_encode_filename(fname)  # encode the filename
                        fancy_url = settings.ROOTURL + "fancy/" + path_txt  # create the invisible encoded url
                        discord_url = settings.ROOTURL + "discord/" + path_txt  # create the invisible encoded url

                        if settings.SAVELOG != "/dev/null":
                            print("Saving to savelog")
                            log_savelog(request.form["uploadKey"], request.remote_addr, fname)

                        print("Returning json response")
                        return jsonify({'status'        : 'success',
                                        'url'           : url,          # ex. https://example.com/AbcD1234.png
                                        'fancy_url'     : fancy_url,    # invisible encoded form
                                        'discord_url'   : discord_url,  # fancy_url but also embed instead of direct file
                                        'name'          : fname,        # filename
                                        'uploadedName'  : f.filename,   # name that was uploaded
                                        }), status.HTTP_201_CREATED

                    else:  # if the image doesn't exist, somehow
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
    else:  # if the request method wasn't post (this cannot happen)
        print("Somehow the request method was not POST!")
        return jsonify({'status': 'error', 'error': 'WRONG_METHOD'}), status.HTTP_405_METHOD_NOT_ALLOWED

if __name__ == "__main__":
    print("Run with `flask` or a WSGI server!")
