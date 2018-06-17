# btc_wallet.py
# operate Bitcoin wallet with coinbase API
#
# HingOn Miu

# https://developers.coinbase.com/api/v2
# https://github.com/coinbase/coinbase-python

import io
import pycurl
import random
import string
import json
import time
from coinbase.wallet.client import Client


# register coinbase account and enable API keys
# https://developers.coinbase.com/docs/wallet/api-key-authentication
coinbase_api_key = ""
coinbase_api_secret = ""


def send_money(from_address, bitcoin_amount, to_address):
	# create coinbase client with your credentials
	client = Client(coinbase_api_key, coinbase_api_secret)

	# get primary coinbase account
	primary_account = client.get_primary_account()

	# send bitcoin to address
	tx = primary_account.send_money(to=to_address,
	                                amount=bitcoin_amount,
	                                currency="BTC")

	return


def check_address_transactions(bitcoin_address):
	# create coinbase client with your credentials
	client = Client(coinbase_api_key, coinbase_api_secret)

	# get primary coinbase account
	primary_account = client.get_primary_account()

	# list transactions that have been sent to address
	txs = primary_account.get_address_transactions(bitcoin_address)
	transactions = json.loads(txs)["data"]

	# add all bitcoin received
	bitcoin_received = 0.0
	for t in transactions:
		bitcoin_received += float(t["amount"]["amount"])

	return bitcoin_received


def generate_address():
	# create coinbase client with your credentials
	client = Client(coinbase_api_key, coinbase_api_secret)

	# get primary coinbase account
	primary_account = client.get_primary_account()

	# create new address
	address = primary_account.create_address()

	return address



