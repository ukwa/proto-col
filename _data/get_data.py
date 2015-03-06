import json
import requests
import ConfigParser

# Notes
# 
# Collections key should not be quoted, i.e. "1" not "\"1\""
#

config = ConfigParser.ConfigParser()
config.read('act.cfg')

response = requests.post("https://www.webarchive.org.uk/act/login", 
	data={"email": config.get('credentials', 'email'), 
	"password": config.get('credentials','password')})
cookie = response.history[0].headers["set-cookie"]
headers = {
    "Cookie": cookie
}

all = requests.get("https://www.webarchive.org.uk/act/api/collections", headers=headers)
collections_tree = json.loads(all.content)
for c in collections_tree:
	col_url = "https://www.webarchive.org.uk/act/api/collections/%s" % (c['key'].replace("\"",""))
	col_req = requests.get(col_url, headers=headers)
	col = json.loads(col_req.content)
	if col['field_publish'] == True:
		print("Publishing...",c['title'])
		#print(col)
		# Look up all Targets with in this Collection:
		
	else:
		print("Skipping...",c['title'])



