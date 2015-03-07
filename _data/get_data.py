import json
import requests
import ConfigParser
import codecs
import yaml

# Notes
# 
# Collections key should not be quoted, i.e. "1" not "\"1\""
# Collections could include the full collections properties
# Targets do not report collection_cats
# The /api/targets/bycollection/X hook appears to be fully recursive.
# The instances are not available via the API (fix checked in)
# Collection.updatedAt appears to be in milliseconds rather than the usual seconds since epoch.

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
collections_to_publish = []
targets_by_collection = {}
for c in collections_tree:
	c_id = c['key'].replace("\"","")
	col_url = "https://www.webarchive.org.uk/act/api/collections/%s" % c_id
	col_req = requests.get(col_url, headers=headers)
	col = json.loads(col_req.content)
	if col['field_publish'] == True:
		print("Publishing...",c['title'])
		collections_to_publish.append(col)

		# Look up all Targets with in this Collection and add them.
		t_url = "https://www.webarchive.org.uk/act/api/targets/bycollection/%s" % c_id
		t_req = requests.get(t_url, headers=headers)
		targets = json.loads(t_req.content)
		targets_by_collection[c_id] = targets
		col['num_targets'] = len(targets)

		# Make a Collection page:
		with codecs.open('../collections/%s.html' % c_id, 'w', encoding='utf8') as outfile:
			outfile.write("---\n")
			outfile.write("layout: collection\n")
			outfile.write("title: %s\n" % col['name'])
			outfile.write("collection_id: %s\n" % c_id)
			outfile.write("num_targets: %s\n" % col['num_targets'])
			outfile.write("---\n")
			outfile.write(col['description'])

		# Make Target pages:
		for target in targets:
			t_id = target['id']
			t_data = {}
			t_data['layout'] = 'target'
			t_data['title'] = target['title']
			t_data['start_date'] = target['crawlStartDateISO']
			t_data['end_date'] = target['crawlEndDateISO']
			urls = []
			for fieldUrl in target['fieldUrls']:
				urls.append(fieldUrl['url'])
			t_data['urls'] = urls
			t_data['metadata'] = target
			with codecs.open('../targets/%s.html' % t_id, 'w', encoding='utf8') as outfile:
				outfile.write("---\n")
				outfile.write(yaml.safe_dump(t_data, default_flow_style=False) )
				outfile.write("---\n")
				if( target['description'] ):
					outfile.write(target['description'])

	else:
		print("Skipping...",c['title'])	

# And write out:
with open('collections.json', 'w') as outfile:
    json.dump(collections_to_publish, outfile, indent=4)
with open('targets.json', 'w') as outfile:
    json.dump(targets_by_collection, outfile, indent=4)
