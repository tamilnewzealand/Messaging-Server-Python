#!/bin/bash

clear

echo "COMPSYS 302 Python Project Setup Script"

echo "Setting up Python 2.7 virtual environment...."

virtualenv -p /usr/bin/python2.7 my_virtualenv
source my_virtualenv/bin/activate

echo "Installing some packages using pip...."
pip install passlib
pip install scrypt
pip install bcrypt
pip install pycrypto

python main.py

