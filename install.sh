#!/bin/sh


# install pip 
python --version
pip --version
sudo apt-get install python-pip python-dev build-essential
sudo pip install --upgrade pip 
pip --version

# install pipenv
pip install pipenv

# install python requests
pipenv install requests

# install coinbase library
pip install coinbase

# download official monero wallet
wget https://downloads.getmonero.org/cli/linux64
mkdir monero
tar -xjvf linux64 -C monero

# initial synchronize with monero network
cd monero
./monerod
