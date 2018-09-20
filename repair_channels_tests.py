import config
import requests


mode = "get_config"

url = "http://localhost:{}/get_channel_config".format(config.port)
headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = (config.username, config.password)

if mode == "get_config":
	# Get config info for test channel - WORKING
	data = {"name": config.test_channel, "live": "true"}
	r = requests.post(url, headers=headers, auth=auth, data=data)

	print (r.text)
elif mode == "start":
	# Start test channel - WORKING
	data = {"name": config.test_channel, "action": "start"}
	r = requests.post(url, headers=headers, auth=auth, data=data)

	print (r.text)
elif mode == "stop":
	# Start test channel - WORKING
	data = {"name": config.test_channel, "action": "stop"}
	r = requests.post(url, headers=headers, auth=auth, data=data)

	print (r.text)
