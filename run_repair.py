import config
import json
import requests
from _winreg import *

aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)

aKey = OpenKey(aReg, r"SOFTWARE\\ODBC\\ODBC.INI")


def write_log(name, content):
    """Write log with parameterized name."""
    with open("{}.log".format(name), "w") as f:
        f.write(content)


# A bunch of setup stuff
default_dsn = "SEASQLCLUSTER1"
new_dsn = ""

headers = {"Accept": "application/json", "Content-Type": "application/json"}
auth = (config.iguana_username, config.iguana_password)

req = requests.get("http://localhost:{}/dashboard_data?include_machine_info=true&include_remote_servers=true".format(config.port),
                   auth=auth)

data = json.loads(req.text)
all_channels = data["Channels"]
channels = []

for ch_name in all_channels:
	ch_dict = {}
	ch_dict["name"] = ch_name["Channel"]["Name"]
	ch_dict["running"] = ch_name["Channel"]["IsRunning"]
	channels.append(ch_dict)

# Setup is done, let's actually start updating channels
for channel in channels:
	name = channel["name"]
	running = channel["running"]

	#if name != "calebtest":
	#	continue

	for i in range(500):
		try:
			asubkey_name = EnumKey(aKey, i)
			if asubkey_name != name:
				continue
			asubkey = OpenKey(aKey, asubkey_name)
			val = QueryValueEx(asubkey, "server")
			if "cluster1" in val[0].lower():
				new_dsn = "SEASQLCLUSTER1"
			elif "cluster2" in val[0].lower():
				new_dsn = "SEASQLCLUSTER2"
			else:
				new_dsn = default_dsn
				print ("No DSN found for channel {} in registry. Using default...".format(name))

			print ("New DSN found for {}: {}".format(name, new_dsn))
		except Exception as e:
			#print (e)
			continue

	print ("Repairing HL7 channel: {}".format(name))

	# Get config
	print ("Getting config...")
	url = "http://localhost:{}/get_channel_config".format(config.port)
	data = {"name": name, "live": "true"}
	r = requests.post(url, headers=headers, auth=auth, data=data)
	write_log("config", r.text)

	# Get current DSN and ask if it's good to replace
	cur_dsn = r.text.split("datasource=")[1].split()[0]

    # Wait -- if no changes will take place, just skip this channel.
	if cur_dsn == "\"{}\"".format(new_dsn):
		print ("Current DSN {} == desired DSN {}. Skipping.").format(cur_dsn, new_dsn)
		print ("------------------------------\n")
		continue

	new_config = r.text.replace("datasource={}".format(cur_dsn),
                                "datasource=\"{}\"".format(new_dsn))
	print ("Current DSN for {}: {}.".format(name, cur_dsn))
	print ("Ready to stop channel, replace {} with \"{}\", and restart channel.".format(cur_dsn, new_dsn))

	# Get user input: "go" to continue, "skip" to...skip
    opt = ""
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
