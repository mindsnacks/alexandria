import requests
import argparse
import json
import itertools
import os


parser = argparse.ArgumentParser(description="Post a build to Alexandria")
parser.add_argument('data_pairs', type=str, nargs='*')
parser.add_argument('--host', type=str, default="http://localhost:8000/")
parser.add_argument('-u', '--username', type=str)
parser.add_argument('-k', '--api_key', type=str)
parser.add_argument('-n', '--name', type=str)
args = parser.parse_args()

i = iter(args.data_pairs)
build_args = dict(itertools.izip(i, i))

metadatas = []
for k, v in build_args.iteritems():
	metadatas.append({'category': k, 'value': v})

post_url = args.host + "api/v0/build/?username=%s&api_key=%s" % (args.username, args.api_key)

print "Posting build..."
r = requests.post(post_url, data=json.dumps({"metadata": metadatas, "name": args.name}), headers={'content-type':'application/json'})
if r.status_code >= 400:
	print "Status code was: " + str(r.status_code)
	print "Post returned: \n" + r.text
	exit(1)
build_data = json.loads(r.content)
f = open('build_number', 'w')
f.write(str(build_data["id"]))
f.close()
print "Done"