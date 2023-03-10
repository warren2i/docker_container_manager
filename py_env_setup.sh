#!/bin/bash

# Update package index and install necessary packages
sudo apt-get update
sudo apt-get install python3-pip -y

# Output pip version for verification
pip3 --version

# Install required libs
sudo pip install docker==6.0.1
sudo pip install prettytable==3.6.0
