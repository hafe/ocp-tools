#!/usr/bin/env python

# A tool to determine possible upgrade paths for a given openshift version
# Example usage: get-ocp-upgrade-paths 4.4.6

import json
import sys
import urllib2

if len(sys.argv) != 2:
    sys.exit("error: wrong number of args")

version = sys.argv[1]
major = version.split(".")[0]
minor = version.split(".")[1]


def search(channel):
    print "\nSearching in channel: " + channel

    # Get graph in json
    url = 'https://api.openshift.com/api/upgrades_info/v1/graph?channel=' + \
        channel + '&arch=amd64'
    headers = {'Accept': 'application/json'}
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    raw = response.read()
    data = json.loads(raw)

    version_found = False

    # Find wanted version to get its index in the node list
    for index, node in enumerate(data['nodes']):
        if node['version'] == version:
            version_found = True
            break

    if not version_found:
        sys.exit("error: could not find version: " + version)

    print "found version:", node["version"], "at index:", index

    edge_found = False

    # Print all edges where the from version is our wanted version
    for edge in data['edges']:
        if edge[0] == index:
            print "edge: ", edge
            print "node: "
            print json.dumps(data['nodes'][edge[1]], indent=4, sort_keys=True)
            edge_found = True

    if not edge_found:
        print "==> Could not find upgrade path for: " + \
            version + " in channel: " + channel

    return edge_found


found = search("stable-" + major + "." + minor)

if not found:
    # bump minor version and try another channel
    minor = str(int(minor) + 1)
    channel = "stable-" + major + "." + minor
    search(channel)
