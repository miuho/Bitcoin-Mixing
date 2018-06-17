# btc_to_xmr.py
# convert Bitcoin to Monero
#
# HingOn Miu

# https://shapeshift.io/

import io
import random
import string
import json
import requests


# shapeshift.io API base URL
shapeshiftio_api_url = "https://shapeshift.io/"

# API endpoint
create_order_endpoint = "sendamount/"
query_status_endpoint = "txStat/"
current_price_endpoint = "rate/"
max_limit_endpoint = "limit/"


def check_bitcoin_limit():
  # make GET request to shapeshift.io to check bitcoin to monero max limit
  response = requests.get(shapeshiftio_api_url + max_limit_endpoint + "btc_xmr")

  # decode json response
  price_response = response.json()

  # limit amount is in bitcoin
  return float(price_response["limit"])


def create_order(monero_amount, monero_address):
  # provide monero destination address and monero amount to send
  payload = {"amount": monero_amount, "pair": "btc_xmr", 
             "withdrawal": monero_address}

  # make POST request to shapeshift.io to create order of sending monero
  response = requests.post(shapeshiftio_api_url + create_order_endpoint, 
                           data=payload)

  # decode json response
  order_response = response.json()

  # bitcoin address for you to send bitcoin for shapeshift.io to convert bitcoin  
  # into monero and send those monero to your monero destination address
  bitcoin_address = order_response["success"]["deposit"]
  # bitcoin amount for you to send
  bitcoin_amount = order_response["success"]["depositAmount"]

  return (float(bitcoin_amount), bitcoin_address)


def query_order_status(bitcoin_address):
  # make GET request to shapeshift.io to query order status
  response = requests.get(shapeshiftio_api_url + query_status_endpoint + bitcoin_address)

  # decode json response
  order_response = response.json()

  # check order status
  order_status = order_response["status"]

  return order_status


def get_price():
  # make GET request to shapeshift.io to check price of 1 bitcoin in monero
  response = requests.get(shapeshiftio_api_url + current_price_endpoint + "btc_xmr")

  # decode json response
  price_response = response.json()

  return float(price_response["rate"])



