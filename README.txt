# Bitcoin-Mixing

Implementation of REST API Bitcoin mixing service by exchanging Bitcoin to Monero and mixing in Monero.

HingOn Miu


Steps:
- Run install.sh to install Python dependencies.

- Run monerod (the Monero daemon) to synchronize and monitor the Monero network.

- Run monero-wallet-rpc to start the Monero wallet service locally on port 18082.

- Run server.py to listen for HTTP connections on port 9000.

- Enter URL in browser or use curl to send HTTP GET requests.

URL Example:
http://127.0.0.1:9000/api?destination_amount=1.5&destination_address=ABC&refund_address=ABC


Documentation:
	Request Mixing Service API
		Request mixing service to break Bitcoin traceability between sender address and
		receiver address. Specify a fixed Bitcoin amount to be sent to the destination
		receiver address. Charge a randomized transaction fee around 2%. Return Bitcoin
		amount user has to deposit and Bitcoin address to deposit to.

		Base URL: "http://127.0.0.1:9000"

		Endpoint: "/api"

		Method: GET

		Parameters:
			$destination_amount:
				Exact Bitcoin amount to be deposited after mixing.

			$destination_address:
				Bitcoin address to deposit destination_amount after mixing.

			$refund_address:
				Bitcoin address for refund if anything goes wrong.

		Full URL:
			http://[HOST]:[PORT]/api?destination_amount=[BTC_AMOUNT]&
				destination_address=[BTC_ADDRESS]&refund_address=[BTC_ADDRESS]

		Success Response:
			200 OK, application/json

		{
			"deposit_amount":  [Exact Bitcoin amount to deposit for service to begin],

			"deposit_address": [Bitcoin address to deposit deposit_amount]
		}



