"""Note: only working with Python2.7 at the moment."""

import config
import requests
import time


mode = "test"
dsn = "SEASQLCLUSTER1" # We want it to be SEASQLCLUSTER1

headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = (config.iguana_username, config.iguana_password)

if mode == "get_config":
	# Get config info for test channel - WORKING
	url = "http://localhost:{}/get_channel_config".format(config.port)
	data = {"name": config.test_channel, "live": "true"}
	r = requests.post(url, headers=headers, auth=auth, data=data)

	print (r.text)
elif mode == "start":
	# Start test channel - WORKING
	url = "http://localhost:{}/status".format(config.port)
	data = {"name": config.test_channel, "action": "start"}
	r = requests.post(url, headers=headers, auth=auth, data=data)

	print (r.text)
elif mode == "stop":
	# Start test channel - WORKING
	url = "http://localhost:{}/status".format(config.port)
	data = {"name": config.test_channel, "action": "stop"}
	r = requests.post(url, headers=headers, auth=auth, data=data)

	print (r.text)
elif mode == "test":
	# Stop test channel, get config, set config, and start test channel

	url = "http://localhost:{}/get_channel_config".format(config.port)
	data = {"name": config.test_channel, "live": "true"}
	r = requests.post(url, headers=headers, auth=auth, data=data)
	print ("Got channel config.")
	raw_input("Press Enter to continue.")

	text = r.text.replace(r.text.split("datasource=")[1].split()[0], "\"{}\"".format(dsn))

	url = "http://localhost:{}/status".format(config.port)
	data = {"name": config.test_channel, "action": "stop"}
	r = requests.post(url, headers=headers, auth=auth, data=data)
	print ("Stopped channel.")
	raw_input("Press Enter to continue.")

	url = "http://localhost:{}/update_channel".format(config.port)
	data = {"config": text}
	r = requests.post(url, headers=headers, auth=auth, data=data)
	print ("Updated channel.")
	raw_input("Press Enter to continue.")

	url = "http://localhost:{}/status".format(config.port)
	data = {"name": config.test_channel, "action": "start"}
	r = requests.post(url, headers=headers, auth=auth, data=data)
	print ("Started channel.")
	raw_input("Press Enter to continue.")

	print text
	#print (r.text)
