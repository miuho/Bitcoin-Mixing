# server.py
# Run http server for bitcoin mixing service
#
# HingOn Miu

# https://docs.python.org/3/library/http.server.html

import io
import random
import string
import json
import time
import socket
import threading
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import mixing_service


# sample http GET url for bitcoin mixing request
# http://127.0.0.1:9000/api?destination_amount=123&destination_address=ABCDEFG&refund_address=ABCDEFG

# api endpoint following base url
API_endpoint = "/api"


class Handler(BaseHTTPRequestHandler):
	# handle http GET requests
	def do_GET(self):
		print("GET: " + self.path)

		# url parameters
		parameters = {
			"destination_amount": 0, # exact bitcoin amount to be deposited after mixing 
			"destination_address": 0, # bitcoin address to deposit destination_amount
			"refund_address": 0	} # refund bitcoin address if mixing service goes wrong

		# parse url path
		parsed_path = urlparse(self.path)
		# check if API endpoint
		if parsed_path.path != API_endpoint:
			self.send_error(404)
			return

		# parse query
		query = parsed_path.query.split("&")
		# check each query
		for q in query:
			# check if format is "A=B"
			kv = q.split("=")
			if len(kv) != 2:
				self.send_error(400)
				return
			k, v = kv
			#print(k)
			#print(v)

			# check if query is a valid parameter
			if k not in parameters:
				self.send_error(400)
				return
			# store value to parameter
			parameters[k] = v

		# check if any parameter is missing
		for v in parameters.values():
			if v == 0:
				self.send_error(400)
				return

		destination_amount = parameters["destination_amount"]
		destination_address = parameters["destination_address"]
		refund_address = parameters["refund_address"]

		# check if bitcoin amount is float
		try:
			float(destination_amount)
		except ValueError:
			self.send_error(400)
			return

		# check bitcoin address format
		if 	(len(destination_address) < 26 or len(destination_address) > 35 or
			len(refund_address) < 26 or len(refund_address) > 35):
			self.send_error(400)
			return

		print("destination_amount: " + destination_amount)
		print("destination_address: " + destination_address)
		print("refund_address: " + refund_address)

		# create mixing service that eventually send destination_amount to destination_address
		# user should first pay service_bill to service_address for mixing service to begin
		service_bill, service_address = \
			mixing_service.create_service(float(destination_amount), destination_address, refund_address)

		self.send_response(200)
		self.send_header("Content-Type", "text/plain; charset=utf-8")
		self.end_headers()
		# request bitcoin amount cannot be handled
		if service_bill == 0.0:
			message = json.dumps({"error": "destination_amount exceeds service maximum limit"})
		else:
			message = json.dumps({"deposit_amount": service_bill, "deposit_address": service_address})
		self.wfile.write(message.encode('utf-8'))
		self.wfile.write(b'\n')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass


if __name__ == "__main__":
	HOST, PORT = "localhost", 9000
	# create server
	server = ThreadedHTTPServer((HOST, PORT), Handler)
	# start server thread to handle requests and server thread starts new thread for each new request
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.daemon = True
	server_thread.start()
	print("Server thread ready to handle http requests...")

	# run main loop of mixing service to monitor all mixing orders
	mixing_service.loop_service()

	# clean up server
	server.shutdown()
	server.server_close()



