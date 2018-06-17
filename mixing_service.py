# service.py
# Run bitcoin mixing service
#
# HingOn Miu


import io
import time
import random
import string
import json
import requests
import btc_to_xmr
import xmr_to_btc
import btc_wallet
import xmr_wallet


# all orders
orders = {}

# 2% service fee in bitcoin
service_fee = 0.02


# keep track of incoming order
class Order:
  # total order number
  total_order_count = 0

  def __init__(self, output_address, refund_address):
    # customer refund address if service unsuccessful
    self.bitcoin_refund_address = refund_address
    # total bitcoin amount deposited by customer
    self.bitcoin_input_amount = 0.0
    # inital bitcoin address for customer desposit from service
    self.bitcoin_input_address = ""
    # final bitcoin destination customer provided
    self.bitcoin_output_address = output_address
    # server monero wallet payment id
    self.xmr_payment_id = ""
    # monero amount to xmr.to
    self.monero_xmrto_amount = 0.0
    # monero address of xmr.to
    self.monero_xmrto_address = ""
    # bitcoin amount to shapeshift.io
    self.bitcoin_shapeshift_amount = 0.0
    # bitcoin address of shapeshift.io
    self.bitcoin_shapeshift_address = ""
    # xmr.to order id
    self.xmr_to_btc_order_id = ""
    # record order create time
    self.created_time = time.time()
    # expires after 10 minutes
    self.expire_time = self.created_time + 600
    # create order id
    self.id = Order.total_order_count
    # track order status: created, expired, paid, forwarded, completed
    self.status = "created"
    # track total orders
    Order.total_order_count += 1

  def check_expired(self):
    # check if order is expired
    if (self.status == "created" and
        time.time() > self.expire_time):
      self.status = "expired"
      return True
    else:
      return False

  def complete(self):
    # signal order is completed
    self.status = "completed"
    return

  def is_fully_paid(self, bitcoin_received):
    # check if bitcoin amount is fully paid
    if bitcoin_received >= self.bitcoin_input_amount:
      self.status = "paid"
      return True
    else:
      return False

  def is_fully_returned(self, monero_received):
    # check if monero amount is fully returned
    if monero_received >= self.monero_xmrto_amount:
      self.status = "forwarded"
      return True
    else:
      return False

  def get_created_time(self):
    return self.created_time

  def get_refund_address(self):
    return self.bitcoin_refund_address

  def set_monero_xmrto_amount(self, monero_amount):
    self.monero_xmrto_amount = monero_amount

  def get_monero_xmrto_amount(self):
    return self.monero_xmrto_amount

  def set_monero_xmrto_address(self, monero_address):
    self.monero_xmrto_address = monero_address

  def get_monero_xmrto_address(self):
    return self.monero_xmrto_address

  def set_xmr_payment_id(self, payment_id):
    self.xmr_payment_id = payment_id

  def get_xmr_payment_id(self):
    return self.xmr_payment_id

  def set_bitcoin_input_amount(self, bitcoin_amount):
    self.bitcoin_input_amount = bitcoin_amount

  def get_bitcoin_input_amount(self):
    return self.bitcoin_input_amount

  def set_bitcoin_input_address(self, input_address):
    self.bitcoin_input_address = input_address

  def get_bitcoin_input_address(self):
    return self.bitcoin_input_address

  def get_id(self):
    return self.id

  def get_status(self):
    return self.status

  def set_bitcoin_shapeshift_amount(self, bitcoin_amount):
    self.bitcoin_shapeshift_amount = bitcoin_amount

  def get_bitcoin_shapeshift_amount(self):
    return self.bitcoin_shapeshift_amount

  def set_bitcoin_shapeshift_address(self, bitcoin_address):
    self.bitcoin_shapeshift_address = bitcoin_address

  def get_bitcoin_shapeshift_address(self):
    return self.bitcoin_shapeshift_address

  def set_xmr_to_btc_order_id(self, order_id):
    self.xmr_to_btc_order_id = order_id

  def get_xmr_to_btc_order_id(self):
    return self.xmr_to_btc_order_id


def initiate_shapeshift(order_id):
  print("Initiate ShapeShift")

  # fetch order
  order = orders[order_id]
  print("  Order ID: " + str(order_id))

  # send shapeshift.io the required bitcoin amount
  bitcoin_amount = order.get_bitcoin_shapeshift_amount()
  bitcoin_address = order.get_bitcoin_shapeshift_address() # to
  my_bitcoin_address = order.get_bitcoin_input_address() # from
  btc_wallet.send_money(my_bitcoin_address, bitcoin_amount, bitcoin_address)
  print("  Sent: " + str(bitcoin_amount) + " BTC")
  
  return


def monitor_shapeshift(order_id):
  print("Monitor ShapeShift")

  # fetch order
  order = orders[order_id]
  print("  Order ID: " + str(order_id))

  # get shapeshift.io deposit bitcoin address
  bitcoin_address = order.get_bitcoin_shapeshift_address()

  # get order status
  btc_to_xmr_order_status = btc_to_xmr.query_order_status(bitcoin_address)
  print("  ShapeShift: " + btc_to_xmr_order_status)

  # check if shapeshift.io returns server requested monero amount
  if btc_to_xmr_order_status != "complete":
    return False

  return True


def initiate_xmrto(order_id):
  print("Initiate XMR.TO")

  # fetch order
  order = orders[order_id]
  print("  Order ID: " + str(order_id))

  # send xmr.to the required monero amount  
  monero_amount = order.get_monero_xmrto_amount()
  monero_address = order.get_monero_xmrto_address() # to
  my_monero_address = "" # from
  xmr_wallet.send_money(my_monero_address, monero_amount, monero_address)
  print("  Sent: " + str(monero_amount) + " XMR")

  return


def monitor_xmrto(order_id):
  print("Monitor XMR.TO")

  # fetch order
  order = orders[order_id]
  print("  Order ID: " + str(order_id))

  # get xmr.to order id
  xmr_to_btc_order_id = order.get_xmr_to_btc_order_id()

  # get order status
  xmr_to_btc_order_status, _ , _ = xmr_to_btc.query_order_status(xmr_to_btc_order_id)
  print("  XMR.TO: " + xmr_to_btc_order_status)

  # check if xmr.to returns requested bitcoin amount to destination address
  if xmr_to_btc_order_status != "BTC_SENT":
    return False
  
  return True


def refund(order_id, bitcoin_amount):
  print("Refund Service")

  # fetch order
  order = orders[order_id]
  print("  Order ID: " + str(order_id))

  # send customer refund
  refund_address = order.get_refund_address() # to
  my_bitcoin_address = order.get_bitcoin_input_address() # from
  btc_wallet.send_money(my_bitcoin_address, bitcoin_amount, refund_address)
  print("  Sent: " + str(bitcoin_amount) + " BTC")

  return


def loop_service():
  while True:
    # loop every 5 seconds
    time.sleep(5)

    # store orders ready to be deleted
    orders_to_delete = list()

    # loop all orders
    for order_id, order in orders.items():

      # check if order is expired
      order.check_expired()

      # check order status
      if order.get_status() == "created":
        # check if customer has paid yet
        my_bitcoin_address = order.get_bitcoin_input_address()
        bitcoin_received = btc_wallet.check_address_transactions(my_bitcoin_address)
        print("  Bitcoin Wallet Received: " + str(bitcoin_received) + " BTC")

        if order.is_fully_paid(bitcoin_received):
          # customer has paid, send bitcoin to shapeshift
          initiate_shapeshift(order_id)

      elif order.get_status() == "paid":
        # sent bitcoin to shapeshift, expect shapeshift returns monero to server 
        if monitor_shapeshift(order_id) == True:

            # check server monero wallet to verify the monero amount
            xmr_payment_id = order.get_xmr_payment_id()
            monero_received = xmr_wallet.check_address_transactions(xmr_payment_id)
            print("  Monero Wallet Received: " + str(monero_received) + " XMR")

            if order.is_fully_returned(monero_received):
              # shapeshift has returned, forward monero requested to xmr.to
              initiate_xmrto(order_id)

      elif order.get_status() == "forwarded":
        # server received monero, forward monero to xmr.to
        if monitor_xmrto(order_id) == True:
          # update orders to completed
          order.complete()

      elif order.get_status() == "expired":
        # customer pays too late
        my_bitcoin_address = order.get_bitcoin_input_address()
        bitcoin_received = btc_wallet.check_address_transactions(my_bitcoin_address)

        # refund customer if partly paid
        if bitcoin_received != 0.0:
          refund(order_id, bitcoin_received)
        
        # update expired orders to completed
        order.complete()

      else:
        # order.get_status() == "completed"
        # mark the order ready to be purged after one hour
        if (time.time() > (order.get_created_time() + 3600)):
          orders_to_delete.append(order_id)

    # purge the completed order after one hour
    for order_id in orders_to_delete:
      del orders[order_id]

    # empty the deleted orders
    orders_to_delete.clear()

  return


def create_service(destination_bitcoin_amount, destination_bitcoin_address,
                   refund_bitcoin_address):
  print("Create Service")

  # check if the bitcoin amount can be handled by xmr.to and shapeshift.io
  if (destination_bitcoin_amount > xmr_to_btc.check_bitcoin_limit() or
    destination_bitcoin_amount > btc_to_xmr.check_bitcoin_limit()):
    return 0.0, ""

  # create new order
  order = Order(destination_bitcoin_address, refund_bitcoin_address)
  print("  Order ID: " + str(order.get_id()))

  # generate a new bitcoin address for customer to deposit
  my_bitcoin_address = btc_wallet.generate_address()
  order.set_bitcoin_input_address(my_bitcoin_address)
  print("  Bitcoin Deposit Address: " + my_bitcoin_address)

  # contact xmr.to to create order that converts monero to bitcoin
  xmr_to_btc_order_id = xmr_to_btc.create_order(destination_bitcoin_amount, 
                                                destination_bitcoin_address)
  order.set_xmr_to_btc_order_id(xmr_to_btc_order_id)

  # get the exact monero amount needed and monero address to send xmr.to
  xmr_to_btc_order_status, monero_amount, monero_address = \
    xmr_to_btc.query_order_status(xmr_to_btc_order_id)
  order.set_monero_xmrto_amount(monero_amount)
  order.set_monero_xmrto_address(monero_address)
  print("  Monero Amount: " + str(monero_amount) + " XMR")

  # generate a new monero address for intermediary transfer
  xmr_payment_id, my_monero_address = xmr_wallet.generate_address()
  order.set_xmr_payment_id(xmr_payment_id)
  print("  Monero Intermediary Address: " + my_monero_address)
  
  # contact shapeshift.io to create order that converts bitcoin to monero
  bitcoin_amount, bitcoin_address = btc_to_xmr.create_order(monero_amount, my_monero_address)
  order.set_bitcoin_shapeshift_amount(bitcoin_amount)
  order.set_bitcoin_shapeshift_address(bitcoin_address)
  print("  Bitcoin Amount: " + str(bitcoin_amount) + " BTC")

  # calculate order service fee
  # cover bitcoin transaction fee from server to shapeshift.io
  # and monero transaction fee from server to xmr.to
  bitcoin_amount_with_fee = bitcoin_amount * (1.0 + service_fee)
  print("  Total With Service Fee: " + str(bitcoin_amount_with_fee) + " BTC")
  order.set_bitcoin_input_amount(bitcoin_amount_with_fee)

  # store order
  orders[order.get_id()] = order

  return bitcoin_amount_with_fee, my_bitcoin_address



