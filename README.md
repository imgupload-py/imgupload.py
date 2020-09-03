# imgupload
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/BBaoVanC/imgupload/master?color=purple) ![GitHub repo size](https://img.shields.io/github/repo-size/bbaovanc/imgupload?color=purple) ![GitHub All Releases](https://img.shields.io/github/downloads/bbaovanc/imgupload/total?color=purple) ![GitHub issues](https://img.shields.io/github/issues/bbaovanc/imgupload?color=purple) ![GitHub closed issues](https://img.shields.io/github/issues-closed/bbaovanc/imgupload?color=purple) ![GitHub](https://img.shields.io/github/license/bbaovanc/imgupload?color=purple)

### What is imgupload?
imgupload is a Flask + uWSGI application to serve as an all-purpose image/file uploader over POST requests.

### Installation
1. Clone the repository: `git clone https://github.com/BBaoVanC/imgupload.git`
2. Enter the imgupload directory: `cd imgupload`
3. Create a virtualenv: `python3 -m venv env`
4. Enter the virtualenv: `source env/bin/activate`
5. Install dependencies: `python3 -m pip install -r requirements.txt`
6. Run the Flask app

### Running the Flask app
## Using uWSGI
[https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html)
Instructions specific to imgupload are coming soon

## Using Flask development server
```shell
$ source env/bin/activate  # if you haven't already entered the virtualenv
$ export FLASK_APP=imgupload.py
$ flask run
```
