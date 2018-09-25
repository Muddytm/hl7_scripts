import config
import json
import requests


def write_log(name, content):
    """Write log with parameterized name."""
    with open("{}.log".format(name), "w") as f:
        f.write(content)


new_dsn = "SEASQLCLUSTER1"

headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = (config.iguana_username, config.iguana_password)

req = requests.get("http://localhost:{}/dashboard_data?include_machine_info=true&include_remote_servers=true".format(config.port),
                   auth=(config.iguana_username, config.iguana_password))

data = json.loads(req.text)
all_channels = data["Channels"]
channels = []

for ch_name in all_channels:
	ch_dict = {}
	ch_dict["name"] = ch_name["Channel"]["Name"]
	ch_dict["running"] = ch_name["Channel"]["IsRunning"]
	channels.append(ch_dict)

for channel in channels:
	name = channel["name"]
	running = channel["running"]
	if name != "calebtest":
		continue

	print ("Repairing HL7 channel: {}".format(name))

	# Get config
	print ("Getting config...")
	url = "http://localhost:{}/get_channel_config".format(config.port)
	data = {"name": name, "live": "true"}
	r = requests.post(url, headers=headers, auth=auth, data=data)
	write_log("config", r.text)

	# Get current DSN and ask if good to go
	cur_dsn = r.text.split("datasource=")[1].split()[0]
	new_config = r.text.replace(cur_dsn, "\"{}\"".format(new_dsn))
	print ("Current DSN for {}: {}.".format(name, cur_dsn))
	print ("Ready to stop channel, replace {} with \"{}\", and restart channel.".format(cur_dsn, new_dsn))

	# Get user input
	opt = raw_input("Type \"go\" to proceed, or \"skip\" to skip this one: ")

	if opt.lower() == "go":
		if running:
			# Stop channel
			print ("Stopping channel...")
			url = "http://localhost:{}/status".format(config.port)
			data = {"name": name, "action": "stop"}
			r = requests.post(url, headers=headers, auth=auth, data=data)
			write_log("stopped", r.text)

			# Update channel
			print ("Updating channel with new DSN config...")
			url = "http://localhost:{}/update_channel".format(config.port)
			data = {"config": new_config}
			r = requests.post(url, headers=headers, auth=auth, data=data)
			write_log("updated", r.text)

			# Start channel
			print ("Starting channel...")
			url = "http://localhost:{}/status".format(config.port)
			data = {"name": name, "action": "start"}
			r = requests.post(url, headers=headers, auth=auth, data=data)
			write_log("started", r.text)
		elif not running:
			print ("Channel is not running. Updating without restarting.")
			write_log("stopped", "none")
			write_log("started", "none")

			# Update channel
			print ("Updating channel with new DSN config...")
			url = "http://localhost:{}/update_channel".format(config.port)
			data = {"config": new_config}
			r = requests.post(url, headers=headers, auth=auth, data=data)
			write_log("updated", r.text)

		# Finished, but check log files.
		print ("Job's done. Check log files to make sure everything worked out.")
		print ("------------------------------\n")
		continue
	else:
		print ("Skipping.")
		print ("------------------------------\n")
		continue
