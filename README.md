# imgupload

[![CodeFactor](https://www.codefactor.io/repository/github/imgupload-py/imgupload.py/badge)](https://www.codefactor.io/repository/github/imgupload-py/imgupload.py)
![GitHub repo size](https://img.shields.io/github/repo-size/imgupload-py/imgupload.py?color=blue)
![GitHub issues](https://img.shields.io/github/issues/imgupload-py/imgupload.py?color=blue)
![GitHub closed issues](https://img.shields.io/github/issues-closed/imgupload-py/imgupload.py?color=blue)
![GitHub license](https://img.shields.io/github/license/imgupload-py/imgupload.py?color=blue)

- [imgupload](#imgupload)
  - [What is imgupload?](#what-is-imgupload)
  - [FAQ](#faq)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
    - [Using uWSGI](#using-uwsgi)
    - [Using Flask development server](#using-flask-development-server)
      - [Setup](#setup)
      - [Run](#run)
  - [License](#license)

## What is imgupload?

imgupload is a Flask + uWSGI application to serve as an all-purpose image uploader over POST requests.

---

## FAQ

**Where can I send bug reports and feature requests?**

You can create an issue [here](https://github.com/BBaoVanC/imgupload/issues).

**How do I use this program?**

See [Installation](#installation)

**I want to make a pull request. Where should I do that?**

First, [fork the repository](https://github.com/BBaoVanC/imgupload/fork). Then, commit your changes to your fork, and create a pull request.

---

## Dependencies

- `python3`
- `python3-pip`
- `python3-venv`
- `git` (for easy updating)

---

## Installation

### Using uWSGI

Note: replace `www-data` with whatever user your webserver runs as.

1. Go to /srv: `cd /srv`
2. Clone the repository: `git clone https://github.com/BBaoVanC/imgupload.git`
3. Change ownership of /srv/imgupload: `sudo chown -R www-data: /srv/imgupload`
4. Enter www-data user: `sudo su www-data`
5. Change directories to /srv/imgupload: `cd /srv/imgupload`
6. Checkout the version you want (replace [version] with desired version tag: `git checkout [version]`
7. Create a virtualenv: `python3 -m venv env`
8. Enter the virtualenv: `source env/bin/activate`
9. Install dependencies: `python3 -m pip install -r requirements.txt`
10. Leave the www-data user: `exit`
11. Copy the default uWSGI configuration: `sudo cp /srv/imgupload/uwsgi.ini.default /etc/uwsgi/apps-available/imgupload.ini`
12. Modify `/etc/uwsgi/apps-available/imgupload.ini` to your preferences
13. Enable imgupload: `sudo ln -s /etc/uwsgi/apps-available/imgupload.ini /etc/uwsgi/apps-enabled/`
14. Restart uWSGI: `sudo systemctl restart uwsgi`
15. Set up your webserver to proxy the uwsgi.sock

Example NGINX location block:

```nginx
location /upload {
    include uwsgi_params;
    uwsgi_pass unix:/srv/imgupload/uwsgi.sock;
    client_max_body_size 25M;
}
```

### Using Flask development server

#### Setup

```shell
git clone https://github.com/BBaoVanC/imgupload.git
cd imgupload
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

#### Run

```shell
export FLASK_APP=imgupload.py
flask run
```

---

## License

_imgupload_ is licensed under the GPLv3 license. For more information, please refer to [`LICENSE`](https://github.com/BBaoVanC/imgupload/blob/master/LICENSE) for more information.
