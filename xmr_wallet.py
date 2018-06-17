# xmr_wallet.py
# operate Monero wallet with official Monero Wallet
#
# HingOn Miu

# https://getmonero.org/resources/developer-guides/wallet-rpc.html

import io
import pycurl
import random
import string
import json
import time
import requests


# create a monero wallet and write down the 25 word mnemonic seed (spend key)
#mnemonic_seed = ""

# wallet information
wallet_address = ""
wallet_username = ""
wallet_password = ""
#view_key = ""

# wallet runs on localhost and port 18082
wallet_url = "http://localhost:18082/json_rpc"
header = {"Content-Type": "application/json"}
rpc_protocol = {"jsonrpc": "2.0", "id": "0"}


def refresh():
	# remember to clear the wallet balance before deleteing the wallet
	# make sure new username is different than old username
	new_wallet_username = str(hash(wallet_username))
	new_wallet_password = wallet_password

	# create a new wallet
	rpc = { "method": "create_wallet",
			"params": {"filename": new_wallet_username,
						"password": new_wallet_password,
						"language": "English"} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)

	# use the new wallet
	rpc = { "method": "open_wallet",
			"params": {"filename": new_wallet_username,
						"password": new_wallet_password} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)

	# get wallet primary address
	rpc = { "method": "getaddress",
			"params": {"account_index": 0} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)
	
	# decode json response
	wallet_response = response.json()

	# replace old wallet information
	wallet_address = wallet_response["result"]["address"]
	wallet_username = new_wallet_username
	wallet_password = new_wallet_password

	return


def send_money(from_address, monero_amount, to_address):
	# send monero amount
	rpc = { "method": "transfer",
			"params": {"destinations": [{"amount": monero_amount, "address": to_address}], 
						"mixin": 4} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)
	
	# decode json response
	transaction_response = response.json()

	# parse transaction information
	transaction_hash = transaction_response["result"]["tx_hash"]

	return transaction_hash


def check_address_transactions(payment_id):
	# get payment information
	rpc = { "method": "get_payments",
			"params": {"payment_id": payment_id} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)
	
	# decode json response
	payment_response = response.json()

	# get all payments
	payments = payment_response["result"]["payments"]

	# add all confirmed monero received
	monero_received = 0.0
	for p in payments:
		#  time (in block height) until this payment is safe to spend
		if p["unlock_time"] == 0:
			monero_received += float(p["amount"])

	return monero_received


def generate_address():
	# unique 16 or 64 character hexadecimal string to track the payment
	# empty string would generate a random payment id
	payment_id = ""

	# get integrated address
	rpc = { "method": "make_integrated_address",
			"params": {"payment_id": payment_id} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)
	
	# decode json response
	address_response = response.json()

	# parse integrated address
	integrated_address = address_response["result"]["integrated_address"]

	# split integrated address to retrieve payment id
	rpc = { "method": "split_integrated_address",
			"params": {"integrated_address": integrated_address} }
	rpc.update(rpc_protocol)

	# make POST request
	response = requests.post(wallet_url, data=json.dumps(rpc), headers=header)
	
	# decode json response
	address_response = response.json()

	# parse payment id
	payment_id = address_response["result"]["payment_id"]

	return payment_id, integrated_address



