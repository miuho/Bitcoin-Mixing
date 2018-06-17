# xmr_to_btc.py
# convert Monero to Bitcoin
#
# HingOn Miu

# https://xmr.to/

import io
import random
import string
import json
import requests


# xmr.to API base URL
xmrto_api_url = "https://xmr.to/api/v2/xmr2btc/"

# API endpoint
create_order_endpoint = "order_create/"
query_status_endpoint = "order_status_query/"
current_price_endpoint = "order_parameter_query/"


def check_bitcoin_limit():
  # make GET request to xmr.to to check monero to bitcoin max limit
  response = requests.get(xmrto_api_url + current_price_endpoint)

  # decode json response
  price_response = response.json()

  # limit amount is in bitcoin
  return float(price_response["upper_limit"])


def create_order(bitcoin_amount, bitcoin_address):
  # provide bitcoin destination address and bitcoin amount to send
  payload = {"btc_amount": bitcoin_amount, "btc_dest_address": bitcoin_address}

  # make POST request to xmr.to to create order of sending bitcoin
  response = requests.post(xmrto_api_url + create_order_endpoint, data=payload)

  # decode json response
  order_response = response.json()

  # check order status
  order_status = order_response["state"]
  if order_status != "TO_BE_CREATED":
    # alert failed to create order
    print(term.format("Create xmr.to Order Failed\n", term.Attr.BOLD))
    return ""

  # placed order id
  order_id = order_response["uuid"]

  return order_id


def query_order_status(order_id):
  # provide order id
  payload = {"uuid": order_id}

  # make POST request to xmr.to to query order status
  response = requests.post(xmrto_api_url + query_status_endpoint, data=payload)

  # decode json response
  order_response = response.json()

  # check order status
  order_status = order_response["state"]

  # monero address for you to send monero for xmr.to to convert monero into 
  # bitcoin and send those bitcoin to your bitcoin destination address
  monero_address = order_response["xmr_receiving_integrated_address"]
  # monero amount for you to send
  monero_amount = order_response["xmr_required_amount"]

  return (order_status, float(monero_amount), monero_address)


def get_price():
  # make GET request to xmr.to to check price of 1 monero in bitcoin
  response = requests.get(xmrto_api_url + current_price_endpoint)

  # decode json response
  price_response = response.json()

  return float(price_response["price"])



