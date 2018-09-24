import config
import json
import requests

req = requests.get("http://localhost:{}/dashboard_data?include_machine_info=true&include_remote_servers=true".format(config.port),
                   auth=(config.iguana_username, config.iguana_password))

data = json.loads(req.text)
channels = data["Channels"]

final = "| NAME         | GROUPS                | PORT    | DATA SOURCE      | RUNNING   |\n"
final += "| ------------ | --------------------- | ------- | ---------------- | --------- |\n"


def get_info(channel):
	req = requests.get("http://localhost:{}//channel_status_data.html?Channel={}".format(config.port, channel),
                       auth=(config.iguana_username, config.iguana_password))
	data = json.loads(req.text)

    # Because even returning JSON is too hard for Iguanaware...
	port_search = data["SourceTooltip"]
	port = (port_search.split("<th nowrap>Port<td nowrap>")[1]).split("<tr><th nowrap>")[0]
	#port = port_search

	dsn_search = data["DestinationTooltip"]
	dsn = (dsn_search.split("<th nowrap>Data source<td nowrap>")[1]).split("<tr><th nowrap>")[0]
	#dsn = dsn_search.split("<tr><th nowrap>")[0]

	return port, dsn


for channel in channels:
	name = channel['Channel']['Name']
	group_list = channel["Channel"]["GroupList"]
	running = channel["Channel"]["IsRunning"]
	port, dsn = get_info(name)
	if int(port) < 27000:
		final += "| {} | {} | {} | {} | {} |\n".format(name,
												       group_list,
													   port,
													   dsn,
													   running)


with open("channel_info.md", "w") as f:
	f.write(final)
